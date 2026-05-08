/**
 * Schoenflies
 * Copyright (c) 2021 Luuk Kempen
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

#ifndef GUI_MAIN_WINDOW_H
#define GUI_MAIN_WINDOW_H

#include <iostream>

#include <memory>
#include <string>
#include <Qt>
#include <QAction>
#include <QActionGroup>
#include <QApplication>
#include <QDialog>
#include <QFileDialog>
#include <QIcon>
#include <QKeySequence>
#include <QMainWindow>
#include <QMenu>
#include <QMenuBar>
#include <QMessageBox>
#include <QMoveEvent>
#include <QObject>
#include <QStatusBar>
#include <QString>
#include "../program.h"
#include "../structure.h"
#include "../structure_renderer.h"
#include "../library/library_item.h"
#include "central_widget.h"
#include "character_table_dialog.h"
#include "gui_mode.h"
#include "library_dialog.h"
#include "stereoscopic_method.h"

class CentralWidget;  // forward declaration

class MainWindow: public QMainWindow {
    Q_OBJECT

private:
    CentralWidget* central_widget;
    LibraryDialog* library_dialog;
    CharacterTableDialog* character_table_dialog = nullptr;

public:
    /**
     * @brief Construct a new Main Window object
     */
    MainWindow();

protected:
    /**
     * @brief Handle window move event
     *
     * @param event
     */
    void moveEvent(QMoveEvent* event) Q_DECL_OVERRIDE;

private:
    /**
     * @brief Load a structure
     *
     * @param filename
     */
    void load_structure(const std::string& filename);

    /**
     * @brief Load a structure
     *
     * @param item
     */
    void load_structure(const LibraryItem& item);

private slots:
    /**
     * @brief Open a new file
     */
    void open();

    /**
     * @brief Open the library dialog
     */
    void open_library_dialog();

    /**
     * @brief Handle the return value of the library dialog
     *
     * @param result dialog result code
     */
    void handle_library_dialog(int result);

    /**
     * @brief Load a random practice structure from the library
     */
    void load_library_practice_structure();

    /**
     * @brief Open the character table dialog
     */
    void open_character_table_dialog();

    /**
     * @brief Close the application
     */
    void exit();

    /**
     * @brief Display about menu
     */
    void about();
};

#endif  // GUI_MAIN_WINDOW_H
