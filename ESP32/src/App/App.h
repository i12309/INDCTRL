#pragma once

class App {
public:
    struct Context {
        bool initialized = false;
    };

    App();

    static App* instance();
    static Context& context();

    void init();
    void process();

private:
    static App* instance_;
    Context context_;
};
