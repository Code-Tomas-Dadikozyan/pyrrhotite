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

// implementation of this class based on https://forum.qt.io/topic/30598/

#ifndef GUI_RICH_TEXT_HEADER_VIEW_H
#define GUI_RICH_TEXT_HEADER_VIEW_H

#include <iostream>

#include <Qt>
#include <QApplication>
#include <QHeaderView>
#include <QPainter>
#include <QRect>
#include <QStyle>
#include <QStyleOptionHeader>
#include <QTextDocument>
#include <QWidget>

class RichTextHeaderView: public QHeaderView {
    Q_OBJECT

public:
    RichTextHeaderView(Qt::Orientation orientation, QWidget *parent = nullptr);

protected:
    /**
     * @brief Paints the section specified by the given logical_index, using
     * the given painter and rect.
     *
     * @param painter
     * @param rect_in
     * @param section_in
     */
    void paintSection(QPainter* painter, const QRect& rect, int logical_index) const;

    /**
     * @brief Returns the size of the contents of the section specified by the
     * given logical_index.
     *
     * @param logical_index
     * @return QSize
     */
    QSize sectionSizeFromContents(int logical_index) const;
};

#endif  // GUI_RICH_TEXT_HEADER_VIEW_H
