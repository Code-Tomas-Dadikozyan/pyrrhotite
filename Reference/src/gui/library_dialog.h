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

#ifndef GUI_LIBRARY_DIALOG_H
#define GUI_LIBRARY_DIALOG_H

#include <memory>
#include <string>
#include <vector>
#include <Qt>
#include <QDialog>
#include <QDialogButtonBox>
#include <QHeaderView>
#include <QLabel>
#include <QLineEdit>
#include <QStandardItem>
#include <QStandardItemModel>
#include <QString>
#include <QTreeView>
#include <QVBoxLayout>
#include <QWidget>
#include "../library/library.h"
#include "../library/library_item.h"
#include "library_item_delegate.h"
#include "library_item_filter_model.h"

class LibraryDialog: public QDialog {
    Q_OBJECT

private:
    QStandardItemModel* model;
    LibraryItemFilterModel* proxy_model;
    QTreeView* tree_view;

    QLineEdit* search_field;

    std::shared_ptr<Library> library;

public:
    /**
     * @brief Construct a new Library Dialog object
     *
     * @param parent
     */
    LibraryDialog(QWidget* parent = nullptr);

    /**
     * @brief Set the library object
     *
     * @param library
     */
    void set_library(const std::shared_ptr<Library>& library);

    /**
     * @brief Get the path to the selected library item, or an empty string if
     * none is selected
     *
     * @return const std::string
     */
    const std::string get_selected_item_path() const;

private:
    /**
     * @brief Update the widget contents
     */
    void update_widget();

private slots:
    /**
     * @brief Triggered when the user double-clicks an item
     *
     * @param index
     */
    void double_click(QModelIndex index);
};

#endif  // GUI_LIBRARY_DIALOG_H
