import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import Lomiri.Components 1.3
import Lomiri.SystemSettings 1.0

ItemPage {
    id: waydroidHelperPage
    header: PageHeader {
        id: pageHeader
        title: i18n.tr("Waydroid Helper")
        subtitle: i18n.tr("Manage your Waydroid containers")
    }

    ScrollView {
        anchors.fill: parent
        anchors.topMargin: pageHeader.height

        Column {
            width: parent.width
            spacing: units.gu(2)
            padding: units.gu(2)

            // Container status
            Card {
                width: parent.width - units.gu(4)
                anchors.horizontalCenter: parent.horizontalCenter
                height: containerStatusColumn.height + units.gu(4)

                Column {
                    id: containerStatusColumn
                    width: parent.width - units.gu(4)
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: units.gu(1)

                    Label {
                        text: i18n.tr("Container Status")
                        fontSize: "large"
                        font.bold: true
                    }

                    Row {
                        width: parent.width
                        spacing: units.gu(1)

                        Label {
                            text: i18n.tr("Status:")
                            width: parent.width / 3
                        }

                        Label {
                            id: containerStatusLabel
                            text: i18n.tr("Stopped")
                            color: text === i18n.tr("Running") ? LomiriColors.green : LomiriColors.red
                        }
                    }

                    Row {
                        width: parent.width
                        spacing: units.gu(2)

                        Button {
                            text: containerStatusLabel.text === i18n.tr("Running") ? i18n.tr("Stop") : i18n.tr("Start")
                            color: containerStatusLabel.text === i18n.tr("Running") ? LomiriColors.red : LomiriColors.green
                            onClicked: {
                                if (containerStatusLabel.text === i18n.tr("Running")) {
                                    // Stop Waydroid
                                    containerStatusLabel.text = i18n.tr("Stopping...")
                                    backendController.stopContainer()
                                } else {
                                    // Start Waydroid
                                    containerStatusLabel.text = i18n.tr("Starting...")
                                    backendController.startContainer()
                                }
                            }
                        }

                        Button {
                            text: i18n.tr("Restart")
                            onClicked: {
                                containerStatusLabel.text = i18n.tr("Restarting...")
                                backendController.restartContainer()
                            }
                        }

                        Button {
                            text: i18n.tr("Freeze")
                            enabled: containerStatusLabel.text === i18n.tr("Running")
                            onClicked: {
                                containerStatusLabel.text = i18n.tr("Freezing...")
                                backendController.freezeContainer()
                            }
                        }
                    }
                }
            }

            // Resource Monitor
            Card {
                width: parent.width - units.gu(4)
                anchors.horizontalCenter: parent.horizontalCenter
                height: resourceMonitorColumn.height + units.gu(4)

                Column {
                    id: resourceMonitorColumn
                    width: parent.width - units.gu(4)
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: units.gu(1)

                    Label {
                        text: i18n.tr("Resource Monitor")
                        fontSize: "large"
                        font.bold: true
                    }

                    Row {
                        width: parent.width
                        spacing: units.gu(1)

                        Label {
                            text: i18n.tr("CPU Usage:")
                            width: parent.width / 3
                        }

                        ProgressBar {
                            id: cpuProgressBar
                            width: parent.width / 2
                            value: 0.0
                        }

                        Label {
                            id: cpuUsageLabel
                            text: "0%"
                        }
                    }

                    Row {
                        width: parent.width
                        spacing: units.gu(1)

                        Label {
                            text: i18n.tr("RAM Usage:")
                            width: parent.width / 3
                        }

                        ProgressBar {
                            id: ramProgressBar
                            width: parent.width / 2
                            value: 0.0
                        }

                        Label {
                            id: ramUsageLabel
                            text: "0 MB"
                        }
                    }

                    Row {
                        width: parent.width
                        spacing: units.gu(1)

                        Label {
                            text: i18n.tr("Storage:")
                            width: parent.width / 3
                        }

                        ProgressBar {
                            id: storageProgressBar
                            width: parent.width / 2
                            value: 0.0
                        }

                        Label {
                            id: storageUsageLabel
                            text: "0 GB"
                        }
                    }
                }
            }

            // App Visibility
            Card {
                width: parent.width - units.gu(4)
                anchors.horizontalCenter: parent.horizontalCenter
                height: appVisibilityColumn.height + units.gu(4)

                Column {
                    id: appVisibilityColumn
                    width: parent.width - units.gu(4)
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: units.gu(1)

                    Label {
                        text: i18n.tr("Android App Visibility")
                        fontSize: "large"
                        font.bold: true
                    }

                    ListModel {
                        id: appModel
                        // Will be populated from backend
                        ListElement { appName: "Example App 1"; packageName: "com.example.app1"; visible: true }
                        ListElement { appName: "Example App 2"; packageName: "com.example.app2"; visible: false }
                    }

                    ListView {
                        width: parent.width
                        height: appModel.count * units.gu(6)
                        model: appModel
                        delegate: ListItem {
                            height: units.gu(6)
                            
                            Row {
                                anchors.fill: parent
                                anchors.margins: units.gu(1)
                                spacing: units.gu(1)
                                
                                Label {
                                    text: appName
                                    width: parent.width * 0.6
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                                
                                Switch {
                                    checked: visible
                                    anchors.verticalCenter: parent.verticalCenter
                                    onToggled: {
                                        backendController.setAppVisibility(packageName, checked)
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Automation Settings
            Card {
                width: parent.width - units.gu(4)
                anchors.horizontalCenter: parent.horizontalCenter
                height: automationColumn.height + units.gu(4)

                Column {
                    id: automationColumn
                    width: parent.width - units.gu(4)
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: units.gu(1)

                    Label {
                        text: i18n.tr("Automation")
                        fontSize: "large"
                        font.bold: true
                    }

                    Row {
                        width: parent.width
                        spacing: units.gu(1)

                        Label {
                            text: i18n.tr("Auto-start Waydroid:")
                            width: parent.width * 0.7
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Switch {
                            id: autoStartSwitch
                            checked: false
                            anchors.verticalCenter: parent.verticalCenter
                            onToggled: {
                                backendController.setAutoStart(checked)
                            }
                        }
                    }

                    Row {
                        width: parent.width
                        spacing: units.gu(1)

                        Label {
                            text: i18n.tr("Check for updates:")
                            width: parent.width * 0.7
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Switch {
                            id: autoUpdateSwitch
                            checked: false
                            anchors.verticalCenter: parent.verticalCenter
                            onToggled: {
                                backendController.setAutoUpdate(checked)
                            }
                        }
                    }

                    Button {
                        text: i18n.tr("Backup Waydroid Data")
                        width: parent.width
                        onClicked: {
                            backendController.backupData()
                        }
                    }

                    Button {
                        text: i18n.tr("Restore Waydroid Data")
                        width: parent.width
                        onClicked: {
                            backendController.restoreData()
                        }
                    }
                }
            }
        }
    }

    // Backend Controller
    QtObject {
        id: backendController

        function startContainer() {
            // Call Python backend
            // This is a placeholder for DBus/C++ integration
            console.log("Starting container")
            // After container starts:
            containerStatusLabel.text = i18n.tr("Running")
            updateResourceUsage()
        }

        function stopContainer() {
            console.log("Stopping container")
            // After container stops:
            containerStatusLabel.text = i18n.tr("Stopped")
            cpuProgressBar.value = 0
            ramProgressBar.value = 0
            cpuUsageLabel.text = "0%"
            ramUsageLabel.text = "0 MB"
        }

        function restartContainer() {
            console.log("Restarting container")
            // After container restarts:
            containerStatusLabel.text = i18n.tr("Running")
            updateResourceUsage()
        }

        function freezeContainer() {
            console.log("Freezing container")
            containerStatusLabel.text = i18n.tr("Frozen")
        }

        function updateResourceUsage() {
            // This would normally be called periodically with data from backend
            cpuProgressBar.value = 0.45
            ramProgressBar.value = 0.38
            storageProgressBar.value = 0.72
            cpuUsageLabel.text = "45%"
            ramUsageLabel.text = "380 MB"
            storageUsageLabel.text = "7.2 GB"
        }

        function setAppVisibility(packageName, visible) {
            console.log("Setting visibility for " + packageName + " to " + visible)
        }

        function setAutoStart(enabled) {
            console.log("Setting auto-start to " + enabled)
        }

        function setAutoUpdate(enabled) {
            console.log("Setting auto-update to " + enabled)
        }

        function backupData() {
            console.log("Backing up data")
        }

        function restoreData() {
            console.log("Restoring data")
        }
    }

    Component.onCompleted: {
        // Check container status on load
        // Load user preferences
    }

    Timer {
        interval: 3000
        running: containerStatusLabel.text === i18n.tr("Running")
        repeat: true
        onTriggered: {
            backendController.updateResourceUsage()
        }
    }
}