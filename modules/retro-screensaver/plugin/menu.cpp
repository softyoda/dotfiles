#include <Plasma/ContainmentActions>
#include <KPluginFactory>
#include <KPluginMetaData>
#include <KConfigGroup>
#include <QAction>
#include <QMenu>
#include <QProcess>
#include <QSettings>
class RetroMenu : public Plasma::ContainmentActions {
 Q_OBJECT
 Plasma::ContainmentActions *base=nullptr;
 QMenu *menu;
 public:
 RetroMenu(QObject *parent,const QVariantList &args):ContainmentActions(parent,args) {
  auto meta=KPluginMetaData::findPluginById("plasma/containmentactions","org.kde.contextmenu");
  base=KPluginFactory::instantiatePlugin<Plasma::ContainmentActions>(meta,this,args).plugin;
  menu=new QMenu(QString::fromUtf8("Économiseur d’écran rétro"));
  menu->setIcon(QIcon::fromTheme("preferences-desktop-screensaver"));
  auto settings=menu->addAction(QString::fromUtf8("Choisir les animations et les délais…"));
  connect(settings,&QAction::triggered,this,[]{QProcess::startDetached("xscreensaver-settings",{});});
  auto preview=menu->addAction(QString::fromUtf8("Démarrer maintenant"));
  connect(preview,&QAction::triggered,this,[]{QProcess::startDetached("xscreensaver-command",{"-activate"});});
  menu->addSeparator();
  auto protect=menu->addAction(QString::fromUtf8("Ne pas activer pendant les jeux et films"));
  protect->setCheckable(true);
  connect(menu,&QMenu::aboutToShow,this,[protect]{QSettings s("retro-saver","preferences");protect->setChecked(s.value("protect",true).toBool());});
  connect(protect,&QAction::toggled,this,[](bool checked){QSettings s("retro-saver","preferences");s.setValue("protect",checked);});
 }
 ~RetroMenu() override {delete menu;}
 void restore(const KConfigGroup &g) override {if(base){base->setContainment(containment());base->restore(g);}}
 void save(KConfigGroup &g) override {if(base)base->save(g);}
 QWidget *createConfigurationInterface(QWidget *p) override {return base?base->createConfigurationInterface(p):nullptr;}
 void configurationAccepted() override {if(base)base->configurationAccepted();}
 QList<QAction*> contextualActions() override {
  QList<QAction*> actions;
  if(base){base->setContainment(containment());actions=base->contextualActions();}
  actions.append(menu->menuAction());return actions;
 }
};
K_PLUGIN_CLASS_WITH_JSON(RetroMenu,"menu.json")
#include "menu.moc"
