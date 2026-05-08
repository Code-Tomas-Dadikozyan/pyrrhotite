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

#include "character_table_item_delegate.h"

/**
 * @brief Add optional configuration options to the document object
 *
 * @param doc
 */
void CharacterTableItemDelegate::configure_document(QTextDocument& doc) const {
    if (doc.toRawText().contains("cos")) {
        QFont font = doc.defaultFont();
        font.setPointSizeF(font.pointSizeF() * 0.75);
        doc.setDefaultFont(font);
    }
}
