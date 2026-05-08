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

#ifndef GUI_CHARACTER_TABLE_DIALOG_H
#define GUI_CHARACTER_TABLE_DIALOG_H

#include <cmath>
#include <stdexcept>
#include <Qt>
#include <QDialog>
#include <QHBoxLayout>
#include <QHeaderView>
#include <QItemSelection>
#include <QItemSelectionModel>
#include <QLabel>
#include <QListView>
#include <QMenu>
#include <QModelIndex>
#include <QSizePolicy>
#include <QStandardItem>
#include <QStandardItemModel>
#include <QTableView>
#include <QTreeView>
#include <QVBoxLayout>
#include <QWidget>
#include "../symmetry/irreps/irrep_label.h"
#include "../symmetry/operations/operation_label_count.h"
#include "../symmetry/point_groups/point_group.h"
#include "../symmetry/point_groups/point_group_label.h"
#include "../symmetry/point_groups/point_groups.h"
#include "character_table_item_delegate.h"
#include "point_group_item_delegate.h"
#include "rich_text_header_view.h"

class CharacterTableDialog: public QDialog {
    Q_OBJECT

private:
    QStandardItemModel* point_group_model;
    QTreeView* point_group_view;
    QStandardItemModel* character_table_model;
    QTableView* character_table_view;

public:
    /**
     * @brief Construct a new Character Table Dialog object
     *
     * @param parent
     */
    CharacterTableDialog(QWidget* parent = nullptr);

    /**
     * @brief Show the point group given by the point group label
     *
     * @param label
     */
    void show_point_group(PointGroupLabel label);

    /**
     * @brief Show the point group given by the index
     *
     * @param index
     */
    void show_point_group(unsigned int index);

private:
    /**
     * @brief Add items to the point group model
     */
    void populate_point_groups();

    /**
     * @brief Add items to the character table model
     *
     * @param point_group point group to add items from
     */
    void populate_character_table(PointGroup& point_group);

    /**
     * @brief Add items to the character table model for a linear point group
     * (Cinfv or Dinfh)
     *
     * These items are added manually due to the infinite number of characters;
     * they do not fit in the existing framework.
     *
     * @param point_group
     */
    void populate_character_table_linear(PointGroup& point_group);

    /**
     * @brief Add items to the character table model for the Cinfv point group
     */
    void populate_character_table_Cinfv();

    /**
     * @brief Add items to the character table model for the Dinfh point group
     */
    void populate_character_table_Dinfh();

    /**
     * @brief Update the selection in the point group model
     *
     * @param index index of point group in PointGroups::point_groups
     */
    void update_point_group_selection(unsigned int index);

    /**
     * @brief Format a character coefficient
     *
     * @param number
     * @return QString
     */
    QString format_number(double number);

private slots:
    /**
     * @brief Select a point group from the point group model
     *
     * @param selected
     */
    void select_point_group(const QItemSelection& selected);
};

#endif  // GUI_CHARACTER_TABLE_DIALOG_H
