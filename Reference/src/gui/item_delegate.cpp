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

#include "item_delegate.h"

/**
 * @brief Renders the delegate using the given painter and style option_in
 * for the item specified by index.
 *
 * @param painter
 * @param option_in
 * @param index
 */
void ItemDelegate::paint(QPainter* painter, const QStyleOptionViewItem& option_in, const QModelIndex& index) const {
    QStyleOptionViewItem option = option_in;
    initStyleOption(&option, index);

    if (option.text.isEmpty()) {
        // not handled by this function
        QStyledItemDelegate::paint(painter, option_in, index);
        return;
    }

    QStyle *style = option.widget ? option.widget->style() : QApplication::style();

    QTextOption text_option;
    text_option.setWrapMode(option.features & QStyleOptionViewItem::ViewItemFeature::WrapText ? QTextOption::WrapMode::WordWrap : QTextOption::WrapMode::ManualWrap);
    text_option.setTextDirection(option.direction);

    QTextDocument doc;
    if (option.state & QStyle::StateFlag::State_Selected) {
        QString highlighted_text_colour = option.palette.color(QPalette::ColorRole::HighlightedText).name();
        doc.setDefaultStyleSheet(QString("span {color: %1;}").arg(highlighted_text_colour));
    }
    doc.setDefaultTextOption(text_option);
    doc.setHtml(option.text);
    doc.setDefaultFont(option.font);
    doc.setDocumentMargin(2);
    this->configure_document(doc);
    doc.setTextWidth(option.rect.width());
    doc.adjustSize();

    int max_text_width = this->max_text_width(painter, option, index);

    if (doc.size().width() > max_text_width) {
        // elide text
        QTextCursor cursor(&doc);
        cursor.movePosition(QTextCursor::MoveOperation::End);

        QFontMetrics metric(option.font);

#if QT_VERSION >= QT_VERSION_CHECK(5, 11, 0)
        int ellipsis_width = metric.horizontalAdvance(this->ellipsis);
#else
        int ellipsis_width = metric.width(this->ellipsis);
#endif

        while (doc.size().width() > max_text_width - ellipsis_width) {
            cursor.deletePreviousChar();
            doc.adjustSize();
        }

        cursor.insertText(this->ellipsis);
    }

    // paint item without text (takes care of painting e.g. highlight)
    option.text = QString();
    style->drawControl(QStyle::ControlElement::CE_ItemViewItem, &option, painter, option_in.widget);

    // determine where to render the text (alignment)
    QRect text_rect = style->subElementRect(QStyle::SubElement::SE_ItemViewItemText, &option);
    QSize document_size(doc.size().width(), doc.size().height());  // QSizeF -> QSize
    QRect layout_rect = QStyle::alignedRect(Qt::LayoutDirection::LayoutDirectionAuto, option.displayAlignment, document_size, text_rect);

    painter->save();

    // translate painter to origin of layout rectangle to render text correctly
    painter->translate(layout_rect.topLeft());
    doc.drawContents(painter, text_rect.translated(-text_rect.topLeft()));

    painter->restore();
}

/**
 * @brief Returns the size needed by the delegate to display the item
 * specified by index, taking into account the style information provided
 * by option_in.
 *
 * @param option_in
 * @param index
 * @return QSize
 */
QSize ItemDelegate::sizeHint(const QStyleOptionViewItem& option_in, const QModelIndex& index) const {
    QStyleOptionViewItem option = option_in;
    initStyleOption(&option, index);

    if (option.text.isEmpty()) {
        // not handled by this function
        return QStyledItemDelegate::sizeHint(option_in, index);
    }

    QTextDocument doc;
    doc.setHtml(option.text);
    doc.setTextWidth(option.rect.width());
    doc.setDefaultFont(option.font);
    doc.setDocumentMargin(2);
    this->configure_document(doc);

    return QSize(doc.idealWidth(), doc.size().height());
}

/**
 * @brief Calculate the maximum text width for elision
 *
 * @param painter
 * @param option
 * @param index
 * @return const int
 */
const int ItemDelegate::max_text_width(QPainter* painter, const QStyleOptionViewItem& option, const QModelIndex& index) const {
    return option.rect.width();
}

/**
 * @brief Add optional configuration options to the document object
 *
 * @param doc
 */
void ItemDelegate::configure_document(QTextDocument& doc) const {
    // noop in the default ItemDelegate
}
