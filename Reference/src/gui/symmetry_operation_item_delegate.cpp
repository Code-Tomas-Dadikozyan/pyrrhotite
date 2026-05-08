/**
 * Schoenflies
 * Copyright (c) 2021 Luuk Kempen
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

#include "symmetry_operation_item_delegate.h"

/**
 * @brief Renders the delegate using the given painter and style option_in
 * for the item specified by index.
 *
 * @param painter
 * @param option_in
 * @param index
 */
void SymmetryOperationItemDelegate::paint(QPainter* painter, const QStyleOptionViewItem& option_in, const QModelIndex& index) const {
    ItemDelegate::paint(painter, option_in, index);

    // draw button if data exists in the button role
    if (index.data(ItemDataRole::ButtonRole).toBool()) {
        QStyleOptionButton button;
        button.rect = this->button_rect(option_in);
        button.text = "\u25b6";
        button.state = QStyle::StateFlag::State_Enabled;

        QApplication::style()->drawControl(QStyle::ControlElement::CE_PushButton, &button, painter);
    }
}

/**
 * @brief When editing of an item starts, this function is called with the
 * event that triggered the editing, the model, the index of the item, and
 * the option_in used for rendering the item.
 *
 * @param event
 * @param model
 * @param option_in
 * @param index
 * @return true if event is handled
 */
bool SymmetryOperationItemDelegate::editorEvent(QEvent* event, QAbstractItemModel* model, const QStyleOptionViewItem& option_in, const QModelIndex& index) {
    if (index.data(ItemDataRole::ButtonRole).toBool() && event->type() == QEvent::Type::MouseButtonRelease) {
        QMouseEvent *e = (QMouseEvent *) event;
        QRect button_rect = this->button_rect(option_in);

        if (e->x() >= button_rect.left() && e->x() <= button_rect.right() &&
            e->y() >= button_rect.top() && e->y() <= button_rect.bottom()) {
            model->setData(index, true, ItemDataRole::ButtonClickedRole);
        }
    }

    return false;  // pass through event
}

/**
 * @brief Get rectangle of button
 *
 * @param option_in
 * @return QRect
 */
QRect SymmetryOperationItemDelegate::button_rect(const QStyleOptionViewItem& option_in) const {
    int x, y, w, h;

    x = option_in.rect.right() - option_in.rect.height();
    y = option_in.rect.top();
    w = option_in.rect.height();
    h = option_in.rect.height();

    return QRect(x, y, w, h);
}

/**
 * @brief Calculate the maximum text width for elision
 *
 * @param painter
 * @param option
 * @param index
 * @return const int
 */
const int SymmetryOperationItemDelegate::max_text_width(QPainter* painter, const QStyleOptionViewItem& option, const QModelIndex& index) const {
    return option.rect.width() - (index.data(ItemDataRole::ButtonRole).toBool() ? this->button_rect(option).width() : 0);
}
