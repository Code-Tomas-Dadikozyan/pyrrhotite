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

#ifndef GUI_SYMMETRY_WIDGET_H
#define GUI_SYMMETRY_WIDGET_H

#include <memory>
#include <Qt>
#include <QItemSelection>
#include <QLabel>
#include <QModelIndex>
#include <QModelIndexList>
#include <QStandardItemModel>
#include <QTreeView>
#include <QVBoxLayout>
#include <QVector>
#include <QWidget>
#include "../symmetry/symmetry.h"
#include "../symmetry/operations/operation.h"
#include "symmetry_operation_item_delegate.h"

class SymmetryWidget: public QWidget {
    Q_OBJECT

private:
    QVBoxLayout* layout;
    QLabel* point_group_label;
    QStandardItemModel* model;

    std::shared_ptr<Symmetry> symmetry;

    bool operation_selected = false;
    Operation selected_operation;

public:
    /**
     * @brief Construct a new SymmetryWidget object
     *
     * @param parent pointer to parent widget
     */
    SymmetryWidget(QWidget* parent);

    /**
     * @brief Set the symmetry object
     *
     * @param symmetry
     */
    void set_symmetry(const std::shared_ptr<Symmetry> symmetry);

private:
    /**
     * @brief Update the widget contents
     */
    void update_widget();

public slots:
    /**
     * @brief Request the operation to show in the GL widget based on the
     * selection from the tree view
     */
    void request_operation();

private slots:
    /**
     * @brief Update the operation shown in the GL widget based on the
     * selection from the tree view
     *
     * @param selected information about selected items
     */
    void tree_view_selection_changed(const QItemSelection& selected);

    /**
     * @brief Trigger the animation of a symmetry operation in the GL widget
     *
     * @param index index of symmetry operation in the data model
     */
    void trigger_animation(QModelIndex index);

signals:
    /**
     * @brief Signal to send to start animating an operation
     *
     * @param operation
     */
    void animate_operation(Operation operation);

    /**
     * @brief Signal to send when the selection in the tree view has changed
     *
     * @param operation_selected
     * @param selected_operation
     */
    void operation_changed(bool operation_selected, Operation selected_operation);
};

#endif  // GUI_SYMMETRY_WIDGET_H
