#pragma once

#include <Arduino.h>

class State {
public:
    enum class Type {
        Boot,
        Idle,
        Error,
    };

    explicit State(Type type) : type_(type) {}
    virtual ~State() = default;

    Type type() const { return type_; }

    static void init();
    static void process();
    static void set(State* next);
    static State* current();

protected:
    virtual void onEnter() {}
    virtual State* tick() = 0;

private:
    Type type_;
    static State* current_;
};
