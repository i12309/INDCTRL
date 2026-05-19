#include "Page.h"

namespace Screen {

Page* Page::activePage_ = nullptr;
Page* Page::previousPage_ = nullptr;

Page::Page(ScreensEnum screenId) : screenId_(screenId) {}

void Page::show() {
    prepareOnce();

    if (activePage_ != this) {
        Page* oldPage = activePage_;
        if (oldPage != nullptr) oldPage->onHide();
        previousPage_ = oldPage;
        activePage_ = this;
    }

    loadScreen(screenId_);
    onShow();
}

void Page::hide() {
    if (activePage_ == this) activePage_ = nullptr;
    onHide();
}

void Page::back() {
    (void)restorePrevious(true);
}

bool Page::restorePrevious(bool callOnShow) {
    Page* target = previousPage_;
    if (target == nullptr || target == activePage_) return false;

    previousPage_ = nullptr;
    if (activePage_ != nullptr && activePage_ != target) {
        activePage_->onHide();
    }

    activePage_ = target;
    target->prepareOnce();
    loadScreen(target->screenId_);
    if (callOnShow) target->onShow();
    return true;
}

bool Page::reloadActive(bool callOnShow) {
    if (activePage_ == nullptr) return false;

    activePage_->prepareOnce();
    loadScreen(activePage_->screenId_);
    if (callOnShow) activePage_->onShow();
    return true;
}

void Page::process() {
    if (activePage_ == nullptr) return;
    activePage_->onTick();
}

Page* Page::activePage() {
    return activePage_;
}

Page* Page::previousPage() {
    return previousPage_;
}

void Page::prepareOnce() {
    if (prepared_) return;
    prepared_ = true;
    onPrepare();
}

}  // namespace Screen
