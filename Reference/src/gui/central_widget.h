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

#ifndef GUI_CENTRAL_WIDGET_H
#define GUI_CENTRAL_WIDGET_H

#include <memory>
#include <string>
#include <Qt>
#include <QFrame>
#include <QHBoxLayout>
#include <QList>
#include <QMap>
#include <QModelIndex>
#include <QSizePolicy>
#include <QStackedWidget>
#include <QVBoxLayout>
#include <QWidget>
#include "../library/library.h"
#include "../structure.h"
#include "../symmetry/symmetry.h"
#include "../symmetry/operations/operation.h"
#include "gl_widget.h"
#include "gui_mode.h"
#include "main_window.h"
#include "practice_widget.h"
#include "symmetry_widget.h"

class MainWindow;  // forward declaration

class CentralWidget: public QWidget {
    Q_OBJECT

private:
    GLWidget *gl_widget;
    QStackedWidget *side_widget;
    PracticeWidget *practice_widget;
    SymmetryWidget *symmetry_widget;

    std::shared_ptr<Structure> structure;
    std::shared_ptr<Symmetry> symmetry;
    bool symmetry_set = false;

    std::shared_ptr<Library> library;

    GuiMode gui_mode;

public:
    /**
     * @brief Construct a new Central Widget object
     *
     * @param mw pointer to MainWindow object
     */
    CentralWidget(MainWindow* mw);

    /**
     * @brief Set the structure object
     *
     * @param structure
     */
    void set_structure(std::shared_ptr<Structure> structure);

    /**
     * @brief Set the GUI mode
     *
     * @param action
     */
    void set_gui_mode(QAction* action);

    /**
     * @brief Get the GL widget object
     *
     * @return GLWidget*
     */
    GLWidget* get_gl_widget();

    /**
     * @brief Get whether the symmetry object is set
     *
     * @return true
     * @return false
     */
    bool get_symmetry_set();

    /**
     * @brief Get the symmetry object
     *
     * @return std::shared_ptr<Symmetry>&
     */
    std::shared_ptr<Symmetry>& get_symmetry();

    /**
     * @brief Get the library object
     *
     * @return std::shared_ptr<Library>&
     */
    std::shared_ptr<Library>& get_library();
};

#endif  // GUI_CENTRAL_WIDGET_H
