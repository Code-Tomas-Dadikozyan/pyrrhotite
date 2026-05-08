/**
 * Schoenflies
 * Copyright (c) 2022 Luuk Kempen
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

// implementation of this class based on https://stackoverflow.com/a/66412883

#ifndef GUI_ITEM_DELEGATE_H
#define GUI_ITEM_DELEGATE_H

#include <QApplication>
#include <QModelIndex>
#include <QPainter>
#include <QPalette>
#include <QRect>
#include <QSize>
#include <QString>
#include <QStyle>
#include <QStyledItemDelegate>
#include <QStyleOptionViewItem>
#include <QTextCursor>
#include <QTextDocument>
#include <QTextOption>

class ItemDelegate: public QStyledItemDelegate {
    Q_OBJECT

protected:
    const QString ellipsis = "\u2026";

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
     * @brief Returns the size needed by the delegate to display the item
     * specified by index, taking into account the style information provided
     * by option_in.
     *
     * @param option_in
     * @param index
     * @return QSize
     */
    QSize sizeHint(const QStyleOptionViewItem& option_in, const QModelIndex& index) const;

private:
    /**
     * @brief Calculate the maximum text width for elision
     *
     * @param painter
     * @param option
     * @param index
     * @return const int
     */
    virtual const int max_text_width(QPainter* painter, const QStyleOptionViewItem& option, const QModelIndex& index) const;

    /**
     * @brief Add optional configuration options to the document object
     *
     * @param doc
     */
    virtual void configure_document(QTextDocument& doc) const;
};

#endif  // GUI_ITEM_DELEGATE_H
