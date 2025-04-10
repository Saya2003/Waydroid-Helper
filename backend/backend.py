#!/usr/bin/env python3
import os
import sys
import json
import sqlite3
import subprocess
import psutil
import logging
from pathlib import Path
import time
import threading
import dbus # type: ignore
import dbus.service # type: ignore
import dbus.mainloop.glib # type: ignore
from gi.repository import GLib # type: ignore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/waydroid-helper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('waydroid-helper')

# Constants
DB_PATH = os.path.expanduser('~/.local/share/waydroid-helper/settings.db')
WAYDROID_DATA_PATH = '/var/lib/waydroid'
WAYDROID_APPS_PATH = os.path.expanduser('~/.local/share/applications/waydroid')
BACKUP_PATH = os.path.expanduser('~/Documents/WaydroidBackups')

class WaydroidDBHandler:
    """Handler for database operations"""
    
    def __init__(self, db_path=DB_PATH):
        """Initialize the database handler"""
        self.db_path = db_path
        self._ensure_db_exists()
        
    def _ensure_db_exists(self):
        """Create the database if it doesn't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create settings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        ''')
        
        # Create app_visibility table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_visibility (
            package_name TEXT PRIMARY KEY,
            app_name TEXT,
            visible INTEGER
        )
        ''')
        
        # Create resource_logs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS resource_logs (
            timestamp INTEGER,
            cpu_usage REAL,
            ram_usage REAL,
            storage_usage REAL
        )
        ''')
        
        # Initialize settings if they don't exist
        default_settings = {
            'auto_start': '0',
            'auto_update': '0',
            'last_update_check': str(int(time.time())),
            'last_backup_time': '0'
        }
        
        for key, value in default_settings.items():
            cursor.execute(
                'INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)',
                (key, value)
            )
        
        conn.commit()
        conn.close()
        
    def get_setting(self, key):
        """Get a setting value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else None
    
    def set_setting(self, key, value):
        """Set a setting value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
            (key, str(value))
        )
        
        conn.commit()
        conn.close()
    
    def get_app_visibility(self):
        """Get all app visibility settings"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM app_visibility')
        result = cursor.fetchall()
        
        conn.close()
        return [dict(row) for row in result]
    
    def set_app_visibility(self, package_name, app_name, visible):
        """Set app visibility"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT OR REPLACE INTO app_visibility (package_name, app_name, visible) VALUES (?, ?, ?)',
            (package_name, app_name, 1 if visible else 0)
        )
        
        conn.commit()
        conn.close()
    
    def log_resource_usage(self, cpu_usage, ram_usage, storage_usage):
        """Log resource usage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO resource_logs (timestamp, cpu_usage, ram_usage, storage_usage) VALUES (?, ?, ?, ?)',
            (int(time.time()), cpu_usage, ram_usage, storage_usage)
        )
        
        # Keep only the last 100 log entries
        cursor.execute(
            'DELETE FROM resource_logs WHERE rowid NOT IN (SELECT rowid FROM resource_logs ORDER BY timestamp DESC LIMIT 100)'
        )
        
        conn.commit()
        conn.close()

class WaydroidController:
    """Controls Waydroid container operations"""
    
    def __init__(self, db_handler):
        """Initialize the Waydroid controller"""
        self.db_handler = db_handler
        
    def is_container_running(self):
        """Check if the Waydroid container is running"""
        try:
            output = subprocess.check_output(['waydroid', 'status']).decode('utf-8')
            return 'RUNNING' in output
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            logger.error("Waydroid command not found. Is Waydroid installed?")
            return False
    
    def start_container(self):
        """Start the Waydroid container"""
        try:
            subprocess.Popen(['waydroid', 'session', 'start'])
            return True
        except Exception as e:
            logger.error(f"Failed to start container: {e}")
            return False
    
    def stop_container(self):
        """Stop the Waydroid container"""
        try:
            subprocess.run(['waydroid', 'session', 'stop'], check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to stop container: {e}")
            return False
    
    def restart_container(self):
        """Restart the Waydroid container"""
        try:
            self.stop_container()
            time.sleep(2)  # Wait for container to fully stop
            self.start_container()
            return True
        except Exception as e:
            logger.error(f"Failed to restart container: {e}")
            return False
    
    def freeze_container(self):
        """Freeze the Waydroid container"""
        try:
            subprocess.run(['waydroid', 'container', 'freeze'], check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to freeze container: {e}")
            return False
    
    def unfreeze_container(self):
        """Unfreeze the Waydroid container"""
        try:
            subprocess.run(['waydroid', 'container', 'unfreeze'], check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to unfreeze container: {e}")
            return False
    
    def get_container_resource_usage(self):
        """Get the container's resource usage"""
        cpu_usage = 0.0
        ram_usage = 0.0
        storage_usage = 0.0
        
        try:
            # Get CPU and RAM usage from processes
            waydroid_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'waydroid' in proc.info['name'].lower() or \
                   any('waydroid' in cmd.lower() for cmd in proc.info['cmdline'] if cmd):
                    waydroid_processes.append(proc)
            
            # Calculate CPU usage
            total_cpu = 0.0
            for proc in waydroid_processes:
                try:
                    total_cpu += proc.cpu_percent(interval=0.1)
                except:
                    pass
            cpu_usage = total_cpu / psutil.cpu_count() if total_cpu > 0 else 0
            
            # Calculate RAM usage
            total_ram = 0.0
            for proc in waydroid_processes:
                try:
                    total_ram += proc.memory_info().rss
                except:
                    pass
            ram_usage = total_ram / (1024 * 1024)  # Convert to MB
            
            # Calculate storage usage
            if os.path.exists(WAYDROID_DATA_PATH):
                storage_usage = self._get_dir_size(WAYDROID_DATA_PATH) / (1024 * 1024 * 1024)  # Convert to GB
        
        except Exception as e:
            logger.error(f"Failed to get resource usage: {e}")
        
        # Log resource usage
        self.db_handler.log_resource_usage(cpu_usage, ram_usage, storage_usage)
        
        return {
            'cpu_usage': cpu_usage,
            'ram_usage': ram_usage,
            'storage_usage': storage_usage
        }
    
    def _get_dir_size(self, path):
        """Get the total size of a directory in bytes"""
        total = 0
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += self._get_dir_size(entry.path)
        return total
    
    def get_installed_apps(self):
        """Get a list of installed Android apps"""
        apps = []
        
        try:
            if os.path.exists(WAYDROID_APPS_PATH):
                for file_name in os.listdir(WAYDROID_APPS_PATH):
                    if file_name.endswith('.desktop'):
                        file_path = os.path.join(WAYDROID_APPS_PATH, file_name)
                        app_info = self._parse_desktop_file(file_path)
                        if app_info:
                            apps.append(app_info)
        except Exception as e:
            logger.error(f"Failed to get installed apps: {e}")
        
        return apps
    
    def _parse_desktop_file(self, file_path):
        """Parse a .desktop file to extract app information"""
        app_info = {}
        package_name = ''
        app_name = ''
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if line.startswith('Name='):
                        app_name = line.strip()[5:]
                    elif line.startswith('Exec='):
                        exec_cmd = line.strip()[5:]
                        if 'waydroid app launch' in exec_cmd:
                            package_name = exec_cmd.split(' ')[-1]
            
            if package_name and app_name:
                app_info = {
                    'package_name': package_name,
                    'app_name': app_name,
                    'desktop_file': os.path.basename(file_path)
                }
        except Exception as e:
            logger.error(f"Failed to parse desktop file {file_path}: {e}")
        
        return app_info
    
    def set_app_visibility(self, package_name, app_name, visible):
        """Set app visibility in the app drawer"""
        try:
            # Store visibility setting in the database
            self.db_handler.set_app_visibility(package_name, app_name, visible)
            
            # Find the desktop file
            desktop_files = []
            if os.path.exists(WAYDROID_APPS_PATH):
                for file_name in os.listdir(WAYDROID_APPS_PATH):
                    if file_name.endswith('.desktop'):
                        file_path = os.path.join(WAYDROID_APPS_PATH, file_name)
                        with open(file_path, 'r') as f:
                            content = f.read()
                            if package_name in content:
                                desktop_files.append(file_path)
            
            # Update NoDisplay property in desktop files
            for file_path in desktop_files:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                
                no_display_found = False
                with open(file_path, 'w') as f:
                    for line in lines:
                        if line.startswith('NoDisplay='):
                            f.write(f'NoDisplay={str(not visible).lower()}\n')
                            no_display_found = True
                        else:
                            f.write(line)
                    
                    if not no_display_found:
                        f.write(f'NoDisplay={str(not visible).lower()}\n')
            
            return True
        except Exception as e:
            logger.error(f"Failed to set app visibility: {e}")
            return False
    
    def backup_data(self):
        """Backup Waydroid data"""
        try:
            # Create backup directory if it doesn't exist
            os.makedirs(BACKUP_PATH, exist_ok=True)
            
            # Create a timestamped backup directory
            timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')
            backup_dir = os.path.join(BACKUP_PATH, f'waydroid_backup_{timestamp}')
            os.makedirs(backup_dir, exist_ok=True)
            
            # Stop container if it's running
            was_running = self.is_container_running()
            if was_running:
                self.stop_container()
            
            # Backup Waydroid data
            if os.path.exists(WAYDROID_DATA_PATH):
                backup_cmd = [
                    'sudo', 'tar', 'czf',
                    os.path.join(backup_dir, 'waydroid_data.tar.gz'),
                    '-C', os.path.dirname(WAYDROID_DATA_PATH),
                    os.path.basename(WAYDROID_DATA_PATH)
                ]
                subprocess.run(backup_cmd, check=True)
            
            # Backup app desktop files
            if os.path.exists(WAYDROID_APPS_PATH):
                backup_cmd = [
                    'tar', 'czf',
                    os.path.join(backup_dir, 'waydroid_apps.tar.gz'),
                    '-C', os.path.dirname(WAYDROID_APPS_PATH),
                    os.path.basename(WAYDROID_APPS_PATH)
                ]
                subprocess.run(backup_cmd, check=True)
            
            # Save backup info
            self.db_handler.set_setting('last_backup_time', int(time.time()))
            
            # Restart container if it was running
            if was_running:
                self.start_container()
            
            return True
        except Exception as e:
            logger.error(f"Failed to backup data: {e}")
            return False
    
    def restore_data(self, backup_dir=None):
        """Restore Waydroid data from backup"""
        try:
            # If no backup directory is specified, use the most recent one
            if not backup_dir:
                backup_dirs = [os.path.join(BACKUP_PATH, d) for d in os.listdir(BACKUP_PATH)
                              if os.path.isdir(os.path.join(BACKUP_PATH, d))]
                if not backup_dirs:
                    logger.error("No backup found")
                    return False
                backup_dir = max(backup_dirs, key=os.path.getmtime)
            
            # Check if backup files exist
            data_backup = os.path.join(backup_dir, 'waydroid_data.tar.gz')
            apps_backup = os.path.join(backup_dir, 'waydroid_apps.tar.gz')
            
            if not os.path.exists(data_backup) and not os.path.exists(apps_backup):
                logger.error("No valid backup files found")
                return False
            
            # Stop container if it's running
            was_running = self.is_container_running()
            if was_running:
                self.stop_container()
            
            # Restore Waydroid data
            if os.path.exists(data_backup):
                restore_cmd = [
                    'sudo', 'tar', 'xzf', data_backup,
                    '-C', os.path.dirname(WAYDROID_DATA_PATH)
                ]
                subprocess.run(restore_cmd, check=True)
            
            # Restore app desktop files
            if os.path.exists(apps_backup):
                # Create target directory if it doesn't exist
                os.makedirs(os.path.dirname(WAYDROID_APPS_PATH), exist_ok=True)
                
                restore_cmd = [
                    'tar', 'xzf', apps_backup,
                    '-C', os.path.dirname(WAYDROID_APPS_PATH)
                ]
                subprocess.run(restore_cmd, check=True)
            
            # Restart container if it was running
            if was_running:
                self.start_container()
            
            return True
        except Exception as e:
            logger.error(f"Failed to restore data: {e}")
            return False

class WaydroidDBusService(dbus.service.Object):
    """DBus service for the Waydroid Helper"""
    
    def __init__(self, waydroid_controller, db_handler):
        """Initialize the DBus service"""
        self.waydroid_controller = waydroid_controller
        self.db_handler = db_handler
        
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus_name = dbus.service.BusName(
            'com.ubuntu.WaydroidHelper',
            bus=dbus.SessionBus()
        )
        dbus.service.Object.__init__(
            self,
            bus_name,
            '/com/ubuntu/WaydroidHelper'
        )
        
        # Start resource monitoring thread
        self.monitoring = False
        self.monitor_thread = None
        self._start_resource_monitoring()
    
    def _start_resource_monitoring(self):
        """Start resource monitoring in a separate thread"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._resource_monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
    
    def _resource_monitor_loop(self):
        """Monitor resource usage periodically"""
        while self.monitoring:
            try:
                if self.waydroid_controller.is_container_running():
                    resource_usage = self.waydroid_controller.get_container_resource_usage()
                    self.ResourceUsageChanged(
                        resource_usage['cpu_usage'],
                        resource_usage['ram_usage'],
                        resource_usage['storage_usage']
                    )
            except Exception as e:
                logger.error(f"Error in resource monitor loop: {e}")
            time.sleep(3)  # Check every 3 seconds

    @dbus.service.method('com.ubuntu.WaydroidHelper', in_signature='', out_signature='b')
    def StartContainer(self):
        """Start the Waydroid container"""
        return self.waydroid_controller.start_container()

    @dbus.service.method('com.ubuntu.WaydroidHelper', in_signature='', out_signature='b')
    def StopContainer(self):
        """Stop the Waydroid container"""
        return self.waydroid_controller.stop_container()

    @dbus.service.method('com.ubuntu.WaydroidHelper', in_signature='', out_signature='b')
    def RestartContainer(self):
        """Restart the Waydroid container"""
        return self.waydroid_controller.restart_container()

    @dbus.service.method('com.ubuntu.WaydroidHelper', in_signature='', out_signature='b')
    def FreezeContainer(self):
        """Freeze the Waydroid container"""
        return self.waydroid_controller.freeze_container()

    @dbus.service.method('com.ubuntu.WaydroidHelper', in_signature='', out_signature='b')
    def UnfreezeContainer(self):
        """Unfreeze the Waydroid container"""
        return self.waydroid_controller.unfreeze_container()

    @dbus.service.method('com.ubuntu.WaydroidHelper', in_signature='', out_signature='a{sv}')
    def GetResourceUsage(self):
        """Get the current resource usage"""
        return self.waydroid_controller.get_container_resource_usage()

    @dbus.service.method('com.ubuntu.WaydroidHelper', in_signature='', out_signature='aa{sv}')
    def GetInstalledApps(self):
        """Get a list of installed Android apps"""
        return self.waydroid_controller.get_installed_apps()

    @dbus.service.method('com.ubuntu.WaydroidHelper', in_signature='ssb', out_signature='b')
    def SetAppVisibility(self, package_name, app_name, visible):
        """Set app visibility in the app drawer"""
        return self.waydroid_controller.set_app_visibility(package_name, app_name, visible)

    @dbus.service.method('com.ubuntu.WaydroidHelper', in_signature='', out_signature='b')
    def BackupData(self):
        """Backup Waydroid data"""
        return self.waydroid_controller.backup_data()

    @dbus.service.method('com.ubuntu.WaydroidHelper', in_signature='s', out_signature='b')
    def RestoreData(self, backup_dir):
        """Restore Waydroid data from backup"""
        return self.waydroid_controller.restore_data(backup_dir)

    @dbus.service.method('com.ubuntu.WaydroidHelper', in_signature='', out_signature='b')
    def IsContainerRunning(self):
        """Check if the Waydroid container is running"""
        return self.waydroid_controller.is_container_running()

    @dbus.service.signal('com.ubuntu.WaydroidHelper', signature='ddd')
    def ResourceUsageChanged(self, cpu_usage, ram_usage, storage_usage):
        """Signal emitted when resource usage changes"""
        pass

def main():
    """Main function to start the Waydroid Helper DBus service"""
    db_handler = WaydroidDBHandler()
    waydroid_controller = WaydroidController(db_handler)
    dbus_service = WaydroidDBusService(waydroid_controller, db_handler)

    logger.info("Waydroid Helper DBus service started")
    loop = GLib.MainLoop()
    loop.run()

if __name__ == "__main__":
    main()