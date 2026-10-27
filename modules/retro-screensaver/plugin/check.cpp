#include <QApplication>
#include <KPluginFactory>
#include <KPluginMetaData>
#include <Plasma/ContainmentActions>
#include <iostream>
int main(int argc,char**argv){QApplication app(argc,argv);auto result=KPluginFactory::instantiatePlugin<Plasma::ContainmentActions>(KPluginMetaData(QString::fromLocal8Bit(argv[1])));if(!result.plugin){std::cerr<<result.errorString.toStdString();return 1;} std::cout<<"Plugin and original KDE menu loaded\n";delete result.plugin;}
