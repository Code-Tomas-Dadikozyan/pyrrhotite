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

#ifndef GUI_PRACTICE_WIDGET_H
#define GUI_PRACTICE_WIDGET_H

#include <memory>
#include <stdexcept>
#include <string>
#include <QFrame>
#include <QHBoxLayout>
#include <QList>
#include <QMap>
#include <QPushButton>
#include <QStackedWidget>
#include <QVBoxLayout>
#include <QWidget>
#include "../library/library.h"
#include "../library/library_item.h"
#include "../practice/practice_config.h"
#include "../practice/practice_module.h"
#include "../practice/practice_structure.h"
#include "practice_config_widget.h"
#include "practice_flowchart_widget.h"
#include "practice_irreps_widget.h"
#include "practice_projection_widget.h"

class PracticeWidget: public QWidget {
    Q_OBJECT

private:
    QVBoxLayout* layout;
    QStackedWidget* subwidgets;

    QWidget* buttons_widget;
    QPushButton* stop_button;
    QPushButton* next_button;

    PracticeConfigWidget* config_widget;
    PracticeFlowchartWidget* flowchart_widget;
    PracticeIrrepsWidget* irreps_widget;
    PracticeProjectionWidget *projection_widget;

    std::shared_ptr<PracticeConfig> practice_config;
    std::shared_ptr<PracticeStructure> practice_structure;
    std::shared_ptr<Library> library;

public:
    /**
     * @brief Construct a new PracticeWidget object
     *
     * @param parent pointer to parent widget
     */
    PracticeWidget(QWidget* parent);

    /**
     * @brief Create a practice structure object
     *
     * @param symmetry
     */
    void create_practice_structure(const std::shared_ptr<Symmetry> symmetry);

    /**
     * @brief Set the library object
     *
     * @param library
     */
    void set_library(const std::shared_ptr<Library> library);

private slots:
    /**
     * @brief Configure the practice module and start the practice session
     */
    void start_practice();

    /**
     * @brief Set the practice widget in a state where the exercise is finished
     */
    void finished_exercise();

    /**
     * @brief Stop the current practice session
     */
    void stop_practice();

    /**
     * @brief Create and show a new exercise
     */
    void create_exercise();

signals:
    /**
     * @brief Emitted when a new structure should be loaded from the library
     */
    void request_new_structure();

    /**
     * @brief Open the character table dialog
     */
    void open_character_table_dialog();

    /**
     * @brief Highlight atoms in the GL widget
     *
     * @param atoms atom indices to highlight
     */
    void highlight_atoms(const QList<unsigned int>& atoms);

    /**
     * @brief Label atoms in the GL widget
     *
     * @param labels map of atom indices and labels
     */
    void label_atoms(const QMap<unsigned int, std::string>& labels);
};

#endif  // GUI_PRACTICE_WIDGET_H
