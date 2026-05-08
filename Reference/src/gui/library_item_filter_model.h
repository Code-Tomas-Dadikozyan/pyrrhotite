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

#ifndef GUI_LIBRARY_ITEM_FILTER_MODEL_H
#define GUI_LIBRARY_ITEM_FILTER_MODEL_H

#include <stdexcept>
#include <Qt>
#include <QMetaType>
#include <QModelIndex>
#include <QSortFilterProxyModel>
#include <QString>
#include <QStringList>

class LibraryItemFilterModel: public QSortFilterProxyModel {
    Q_OBJECT

private:
    QString string_filter;

public:
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
    bool filterAcceptsRow(int source_row, const QModelIndex& source_parent) const override;

public slots:
    /**
     * @brief Set the string filter
     *
     * @param string_filter
     */
    void set_string_filter(QString string_filter);
};

#endif  // GUI_LIBRARY_ITEM_FILTER_MODEL_H
