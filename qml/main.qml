import QtQuick 2.7
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1


ApplicationWindow {
    Material.theme: Material.Dark
    Material.accent: Material.Purple
    id: window
    title: "medhack"
    visible: true
    width: 800
    height: 480
    LoudnessIndicator {
        id: micLoudness
        loudness: dialog.micLoudness
        width: 5
        anchors {
            top: parent.top
            bottom: parent.bottom
            left: parent.left
            topMargin: 5
            bottomMargin: 5
            leftMargin: 5
        }
    }
    ListView {
        id: dialogView
        anchors {
            top: parent.top
            left: micLoudness.right
            leftMargin: 5
            right: parent.right
            bottom: startButton.top
        }
        model: dialog.model
        delegate: Rectangle {
            width: parent.width
            height: 50
            color: model.isQuestion ? "blue" : "white"
            Text {
                anchors {
                    verticalCenter: parent.verticalCenter
                    left: model.isQuestion ? parent.left : undefined
                    leftMargin: 10
                    right: !model.isQuestion ? parent.right : undefined
                    rightMargin: 10
                }
                text: model.text
            }
        }
        Component.onCompleted: {
            dialogView.positionViewAtEnd()
        }
    }

    Rectangle {
        id: startButton
        color: "red"
        height: 50
        anchors {
            left: dialogView.left
            right: parent.right
            bottom: parent.bottom
        }

        Text {
            anchors.centerIn: parent
            text: !dialog.inProcess ? "start dialog" : "stop dialog"
        }

        MouseArea {
            anchors.fill: parent
            onClicked: {
                dialog.startDialog()
//                if(!dialog.inProcess) {
//                    dialog.startDialog()
//                } else {
//                    dialog.stopDialog()
//                }
            }
        }
    }
}