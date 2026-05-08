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

#include "symmetry_widget.h"

/**
 * @brief Construct a new SymmetryWidget object
 *
 * @param parent pointer to parent widget
 */
SymmetryWidget::SymmetryWidget(QWidget* parent) {
    this->layout = new QVBoxLayout;
    this->layout->setContentsMargins(0, 0, 0, 0);
    this->setLayout(this->layout);

    this->point_group_label = new QLabel;
    this->point_group_label->setTextFormat(Qt::TextFormat::RichText);
    this->point_group_label->setVisible(false);
    this->layout->addWidget(this->point_group_label);

    QTreeView *tree_view = new QTreeView;
    this->model = new QStandardItemModel;
    SymmetryOperationItemDelegate *delegate = new SymmetryOperationItemDelegate;

    tree_view->setSizePolicy(QSizePolicy::Policy::Minimum, QSizePolicy::Policy::MinimumExpanding);
    tree_view->setMinimumSize(220, 50);
    tree_view->setEditTriggers(QTreeView::EditTrigger::NoEditTriggers);
    tree_view->setMouseTracking(true);
    tree_view->setHeaderHidden(true);
    tree_view->setModel(this->model);
    tree_view->setItemDelegate(delegate);

    connect(this->model, SIGNAL(dataChanged(QModelIndex, QModelIndex, QVector<int>)), this, SLOT(trigger_animation(QModelIndex)));

    QItemSelectionModel *selection_model = tree_view->selectionModel();

    connect(selection_model, SIGNAL(selectionChanged(const QItemSelection&, const QItemSelection&)), this, SLOT(tree_view_selection_changed(const QItemSelection&)));

    this->layout->addWidget(tree_view);
}

/**
 * @brief Set the symmetry object
 *
 * @param symmetry
 */
void SymmetryWidget::set_symmetry(const std::shared_ptr<Symmetry> symmetry) {
    this->symmetry = symmetry;

    this->update_widget();
}

/**
 * @brief Update the widget contents
 */
void SymmetryWidget::update_widget() {
    QString point_group_name = QString::fromStdString(this->symmetry->get_point_group().get_label().get_name_html());
    this->point_group_label->setText(QString("Point group: %1").arg(point_group_name));
    this->point_group_label->setVisible(true);

    this->model->clear();
    QStandardItem *root = this->model->invisibleRootItem();

    const auto operation_manager = this->symmetry->get_operation_manager();
    const auto point_group_operations_order = operation_manager->get_point_group_operations_order();

    // add identity operation, which is always present but not tracked
    root->appendRow(new QStandardItem("<span><i>E</i> identity</span>"));

    // add all other operations
    for (auto operation_group : point_group_operations_order) {
        if (operation_group.get_num_operations() == 1) {
            // add operation on top level
            int operation_id = operation_group.get_operation_ids()[0];
            auto operation = operation_manager->get_point_group_operation(operation_id);

            QStandardItem *item = new QStandardItem(QString("<span>%1</span>").arg(
                QString::fromStdString(operation.get_label().get_name_html())));
            item->setData(operation_id, SymmetryOperationItemDelegate::ItemDataRole::ButtonRole);

            root->appendRow(item);
        } else if (operation_group.get_num_operations() > 1 || operation_group.get_infinite_multiplicity()) {
            // add operation group
            QString title = QString("<span>%1</span>").arg(
                QString::fromStdString(operation_group.get_name_html())
            );
            QStandardItem *item = new QStandardItem(title);

            for (auto operation_id : operation_group.get_operation_ids()) {
                auto operation = operation_manager->get_point_group_operation(operation_id);

                QStandardItem *sub_item = new QStandardItem(QString("<span>%1</span>").arg(
                    QString::fromStdString(operation.get_label().get_name_html())));
                sub_item->setData(operation_id, SymmetryOperationItemDelegate::ItemDataRole::ButtonRole);

                item->appendRow(sub_item);
            }

            root->appendRow(item);
        }
    }
}

/**
 * @brief Request the operation to show in the GL widget based on the
 * selection from the tree view
 */
void SymmetryWidget::request_operation() {
    emit this->operation_changed(this->operation_selected, this->selected_operation);
}

/**
 * @brief Update the operation shown in the GL widget based on the
 * selection from the tree view
 *
 * @param selected information about selected items
 */
void SymmetryWidget::tree_view_selection_changed(const QItemSelection& selected) {
    QModelIndexList indices = selected.indexes();
    if (indices.size() < 1) {
        this->operation_selected = false;
        emit this->operation_changed(this->operation_selected, this->selected_operation);
        return;
    }

    QStandardItem *item = this->model->itemFromIndex(indices[0]);

    if (item->data(SymmetryOperationItemDelegate::ItemDataRole::ButtonRole).toBool()) {
        unsigned int operation_index = item->data(SymmetryOperationItemDelegate::ItemDataRole::ButtonRole).toInt();

        this->selected_operation = this->symmetry->get_operation_manager()->get_point_group_operation(operation_index);
        this->operation_selected = true;
    } else {
        this->operation_selected = false;
    }

    emit this->operation_changed(this->operation_selected, this->selected_operation);
}

/**
 * @brief Trigger the animation of a symmetry operation in the GL widget
 *
 * @param index index of symmetry operation in the data model
 */
void SymmetryWidget::trigger_animation(QModelIndex index) {
    QStandardItem *item = this->model->itemFromIndex(index);

    if (item->data(SymmetryOperationItemDelegate::ItemDataRole::ButtonClickedRole).toBool()) {
        unsigned int operation_index = item->data(SymmetryOperationItemDelegate::ItemDataRole::ButtonRole).toInt();
        Operation operation = this->symmetry->get_operation_manager()->get_point_group_operation(operation_index);

        emit animate_operation(operation);

        item->setData(false, SymmetryOperationItemDelegate::ItemDataRole::ButtonClickedRole);
    }
}
