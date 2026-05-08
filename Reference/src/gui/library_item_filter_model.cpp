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

#include "library_item_filter_model.h"

/**
 * @brief Returns true if the item in the row indicated by the given
 * source_row and source_parent should be included in the model; otherwise
 * returns false.
 *
 * @param source_row
 * @param source_parent
 * @return true
 * @return false
 */
bool LibraryItemFilterModel::filterAcceptsRow(int source_row, const QModelIndex& source_parent) const {
    if (this->string_filter.isEmpty()) return true;

    QModelIndex index = this->sourceModel()->index(source_row, 0, source_parent);
    QString name = sourceModel()->data(index).toString();
    name.remove(0, 6);                // remove "<span>"
    name.remove(name.size() - 7, 7);  // remove "</span>"
    return name.contains(this->string_filter, Qt::CaseSensitivity::CaseInsensitive);
}

/**
 * @brief Set the string filter
 *
 * @param string_filter
 */
void LibraryItemFilterModel::set_string_filter(QString string_filter) {
    this->string_filter = string_filter;

    this->invalidateFilter();
}
