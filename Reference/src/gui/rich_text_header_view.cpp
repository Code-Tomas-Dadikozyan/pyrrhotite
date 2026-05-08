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

#include "rich_text_header_view.h"

RichTextHeaderView::RichTextHeaderView(Qt::Orientation orientation, QWidget *parent)
    : QHeaderView(orientation, parent) {}

/**
 * @brief Paints the section specified by the given logical_index, using
 * the given painter and rect.
 *
 * @param painter
 * @param rect_in
 * @param section_in
 */
void RichTextHeaderView::paintSection(QPainter* painter, const QRect& rect, int logical_index) const {
    if (!rect.isValid()) return;

    QStyleOptionHeader option;
    initStyleOption(&option);

    option.rect = rect;
    option.section = logical_index;
    option.textAlignment = Qt::AlignmentFlag::AlignCenter;

    QTextDocument doc;
    doc.setHtml(this->model()->headerData(logical_index, this->orientation(), Qt::ItemDataRole::DisplayRole).toString());

    // paint item without text (takes care of painting e.g. highlight)
    option.text = QString();
    style()->drawControl(QStyle::ControlElement::CE_Header, &option, painter, this);

    // determine where to render the text (alignment)
    QRect text_rect = style()->subElementRect(QStyle::SubElement::SE_HeaderLabel, &option, this);
    QSize document_size(doc.size().width(), doc.size().height());  // QSizeF -> QSize
    QRect layout_rect = QStyle::alignedRect(Qt::LayoutDirection::LayoutDirectionAuto, option.textAlignment, document_size, text_rect);

    painter->save();
    painter->translate(layout_rect.topLeft());
    doc.drawContents(painter, QRect(QPoint(0, 0), text_rect.size()));
    painter->restore();
}

/**
 * @brief Returns the size of the contents of the section specified by the
 * given logical_index.
 *
 * @param logical_index
 * @return QSize
 */
QSize RichTextHeaderView::sectionSizeFromContents(int logical_index) const {
    QStyleOptionHeader option;
    initStyleOption(&option);

    QTextDocument doc;
    doc.setHtml(this->model()->headerData(logical_index, this->orientation(), Qt::ItemDataRole::DisplayRole).toString());

    return QSize(doc.idealWidth() + 8, doc.size().height() + 4);
}
