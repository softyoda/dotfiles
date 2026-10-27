#include <QApplication>
#include <QGenericPlugin>
#include <QKeyEvent>
#include <QLineEdit>
#include <QTextEdit>
#include <QPlainTextEdit>
#include <QAbstractSpinBox>
#include <QComboBox>
#include <QTimer>

class SpaceAlias : public QObject {
public:
    using QObject::QObject;
    bool eventFilter(QObject* target, QEvent* event) override {
        if (event->type() != QEvent::KeyPress && event->type() != QEvent::KeyRelease)
            return false;
        auto* key = static_cast<QKeyEvent*>(event);
        if (key->key() != Qt::Key_Space || key->modifiers() != Qt::NoModifier)
            return false;
        // Text entry and dialogs retain their standard keyboard behavior.
        if (QApplication::activeModalWidget() || QApplication::activePopupWidget())
            return false;
        for (QWidget* w = QApplication::focusWidget(); w; w = w->parentWidget()) {
            if (qobject_cast<QLineEdit*>(w) || qobject_cast<QTextEdit*>(w) ||
                qobject_cast<QPlainTextEdit*>(w) || qobject_cast<QAbstractSpinBox*>(w) ||
                (qobject_cast<QComboBox*>(w) && static_cast<QComboBox*>(w)->isEditable()))
                return false;
        }
        QKeyEvent replacement(key->type(), Qt::Key_D, key->modifiers(),
            key->nativeScanCode(), key->nativeVirtualKey(), key->nativeModifiers(),
            QStringLiteral("d"), key->isAutoRepeat(), key->count(), key->device());
        QCoreApplication::sendEvent(target, &replacement);
        event->accept();
        return true;
    }
};

class SpaceAliasPlugin : public QGenericPlugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "org.qt-project.Qt.QGenericPluginFactoryInterface" FILE "spacealias.json")
public:
    QObject* create(const QString& key, const QString&) override {
        if (key.compare(QStringLiteral("mixxxspacealias"), Qt::CaseInsensitive)) return nullptr;
        auto* filter = new SpaceAlias();
        // Install after Mixxx's own filters, so Space is translated first.
        QTimer::singleShot(0, filter, [filter] { qApp->installEventFilter(filter); });
        return filter;
    }
};
#include "spacealias.moc"
