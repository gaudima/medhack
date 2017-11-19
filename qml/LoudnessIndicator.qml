import QtQuick 2.1

Rectangle {
    property real loudness: 0
    id: bg
    color: "grey"
    Rectangle {
        id: indicator
        anchors.bottom: parent.bottom
        height: parent.height * bg.loudness
        width: parent.width
        color: "red"
    }
}