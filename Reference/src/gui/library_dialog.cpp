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

#include "library_dialog.h"

LibraryDialog::LibraryDialog(QWidget* parent)
    : QDialog(parent, Qt::WindowType::WindowTitleHint |
                      Qt::WindowType::WindowSystemMenuHint |
                      Qt::WindowCloseButtonHint) {
    this->setWindowTitle("Library");

    QVBoxLayout *layout = new QVBoxLayout;
    this->setLayout(layout);

    this->search_field = new QLineEdit;
    this->search_field->setPlaceholderText("Search in library...");
    layout->addWidget(this->search_field);

    this->tree_view = new QTreeView;
    this->model = new QStandardItemModel;
    this->proxy_model = new LibraryItemFilterModel;
    LibraryItemDelegate *delegate = new LibraryItemDelegate;

    this->proxy_model->setSourceModel(this->model);

    this->tree_view->setMinimumSize(400, 200);
    this->tree_view->setEditTriggers(QTreeView::EditTrigger::NoEditTriggers);
    this->tree_view->setIndentation(0);
    this->tree_view->setItemsExpandable(false);
    this->tree_view->setAllColumnsShowFocus(true);
    this->tree_view->setModel(this->proxy_model);
    this->tree_view->setItemDelegate(delegate);
    // this->tree_view->header()->setSectionResizeMode(QHeaderView::ResizeMode::ResizeToContents);

    connect(this->search_field, SIGNAL(textChanged(QString)), this->proxy_model, SLOT(set_string_filter(QString)));
    connect(this->tree_view, SIGNAL(doubleClicked(QModelIndex)), this, SLOT(double_click(QModelIndex)));

    layout->addWidget(this->tree_view);

    QDialogButtonBox* button_box = new QDialogButtonBox(
        QDialogButtonBox::StandardButton::Ok | QDialogButtonBox::StandardButton::Cancel);

    connect(button_box, SIGNAL(accepted()), this, SLOT(accept()));
    connect(button_box, SIGNAL(rejected()), this, SLOT(reject()));

    layout->addWidget(button_box);

    connect(this, SIGNAL(finished(int)), parent, SLOT(handle_library_dialog(int)));
}

/**
 * @brief Set the library object
 *
 * @param library
 */
void LibraryDialog::set_library(const std::shared_ptr<Library>& library) {
    this->library = library;

    this->update_widget();
}

/**
 * @brief Get the path to the selected library item, or an empty string if
 * none is selected
 *
 * @return const std::string
 */
const std::string LibraryDialog::get_selected_item_path() const {
    QModelIndexList indices = this->tree_view->selectionModel()->selectedIndexes();
    if (indices.size() < 1) {
        return "";
    }

    QStandardItem *item = this->model->itemFromIndex(this->proxy_model->mapToSource(indices[0]));
    return item->data(LibraryItemDelegate::ItemDataRole::PathRole).toString().toStdString();
}

/**
 * @brief Update the widget contents
 */
void LibraryDialog::update_widget() {
    this->model->clear();

    this->model->setHorizontalHeaderLabels({"Structure", "Formula", "Point group"});
    QStandardItem *root = this->model->invisibleRootItem();

    for (const LibraryItem& item : this->library->get_items()) {
        std::vector<std::string> cells = {
            item.get_name(),
            item.get_chemical_formula(),
            item.get_point_group_label().get_name_html()
        };

        QList<QStandardItem*> row;
        for (unsigned int i = 0; i < 3; ++i) {
            QStandardItem* model_item = new QStandardItem(QString("<span>%1</span>").arg(
                QString::fromStdString(cells[i])));
            model_item->setData(QString::fromStdString(item.get_path()),
                LibraryItemDelegate::ItemDataRole::PathRole);

            if (i == 0) {
                model_item->setData(QString::fromStdString(cells[i]), Qt::ItemDataRole::ToolTipRole);
            }

            row.append(model_item);
        }

        root->appendRow(row);
    }

    for (unsigned int i = 0; i < 3; ++i) {
        this->tree_view->resizeColumnToContents(i);
    }
}

/**
 * @brief Triggered when the user double-clicks an item
 *
 * @param index
 */
void LibraryDialog::double_click(QModelIndex index) {
    emit this->accept();
}
