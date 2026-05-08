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

// implementation of this class based on https://stackoverflow.com/a/11778012

#ifndef GUI_SYMMETRY_OPERATION_ITEM_DELEGATE_H
#define GUI_SYMMETRY_OPERATION_ITEM_DELEGATE_H

#include <Qt>
#include <QAbstractItemModel>
#include <QApplication>
#include <QEvent>
#include <QModelIndex>
#include <QMouseEvent>
#include <QPainter>
#include <QRect>
#include <QStyle>
#include <QStyleOptionButton>
#include <QStyleOptionViewItem>
#include "item_delegate.h"

class SymmetryOperationItemDelegate: public ItemDelegate {
    Q_OBJECT

public:
    enum ItemDataRole {
        ButtonRole = Qt::ItemDataRole::UserRole + 1,
        ButtonClickedRole
    };

protected:
    /**
     * @brief Renders the delegate using the given painter and style option_in
     * for the item specified by index.
     *
     * @param painter
     * @param option_in
     * @param index
     */
    void paint(QPainter* painter, const QStyleOptionViewItem& option_in, const QModelIndex& index) const;

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
    bool editorEvent(QEvent* event, QAbstractItemModel* model, const QStyleOptionViewItem& option_in, const QModelIndex& index);

private:
    /**
     * @brief Get rectangle of button
     *
     * @param option_in
     * @return QRect
     */
    QRect button_rect(const QStyleOptionViewItem& option_in) const;

    /**
     * @brief Calculate the maximum text width for elision
     *
     * @param painter
     * @param option
     * @param index
     * @return const int
     */
    const int max_text_width(QPainter* painter, const QStyleOptionViewItem& option, const QModelIndex& index) const override;
};

#endif  // GUI_SYMMETRY_OPERATION_ITEM_DELEGATE_H
