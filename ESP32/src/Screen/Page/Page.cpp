#include "Page.h"

namespace Screen {

Page* Page::activePage_ = nullptr;
Page* Page::previousPage_ = nullptr;

// Сохранить EEZ-идентификатор экрана.
Page::Page(ScreensEnum screenId) : screenId_(screenId) {}

// Показать страницу и обновить стек простого back().
void Page::show() {
    prepareOnce();

    // Если показываем новую страницу, старой даем шанс обработать уход.
    if (activePage_ != this) {
        Page* oldPage = activePage_;
        if (oldPage != nullptr) oldPage->onHide();
        previousPage_ = oldPage;
        activePage_ = this;
    }

    loadScreen(screenId_);
    onShow();
}

// Снять страницу с активной роли.
void Page::hide() {
    if (activePage_ == this) activePage_ = nullptr;
    onHide();
}

// Вернуться на предыдущую страницу.
void Page::back() {
    (void)restorePrevious(true);
}

// Восстановить previousPage после временных экранов вроде Info.
bool Page::restorePrevious(bool callOnShow) {
    Page* target = previousPage_;
    // Некуда возвращаться или предыдущая совпадает с активной страницей.
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

// Перезагрузить активный EEZ-экран, не меняя Page::activePage_.
bool Page::reloadActive(bool callOnShow) {
    if (activePage_ == nullptr) return false;

    activePage_->prepareOnce();
    loadScreen(activePage_->screenId_);
    if (callOnShow) activePage_->onShow();
    return true;
}

// Передать tick активной странице.
void Page::process() {
    if (activePage_ == nullptr) return;
    activePage_->onTick();
}

// Вернуть активную страницу.
Page* Page::activePage() {
    return activePage_;
}

// Вернуть предыдущую страницу.
Page* Page::previousPage() {
    return previousPage_;
}

// Выполнить onPrepare() только один раз за жизнь singleton-страницы.
void Page::prepareOnce() {
    if (prepared_) return;
    prepared_ = true;
    onPrepare();
}

}  // namespace Screen
