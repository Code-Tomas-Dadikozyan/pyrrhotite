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

#ifndef GUI_PRACTICE_FLOWCHART_WIDGET_H
#define GUI_PRACTICE_FLOWCHART_WIDGET_H

#include <memory>
#include <vector>
#include <Qt>
#include <QFrame>
#include <QScrollArea>
#include <QScrollBar>
#include <QSize>
#include <QVBoxLayout>
#include <QWidget>
#include "../practice/practice_flowchart.h"
#include "../practice/practice_structure.h"
#include "practice_flowchart_step_widget.h"

class PracticeFlowchartWidget: public QScrollArea {
    Q_OBJECT

private:
    std::vector<PracticeFlowchartStepWidget*> step_widgets;
    QVBoxLayout *layout;
    QWidget *container;

    std::shared_ptr<PracticeStructure> practice_structure;
    PracticeFlowchart flowchart;

public:
    /**
     * @brief Construct a new PracticeFlowchartWidget object
     *
     * @param parent pointer to parent widget
     */
    PracticeFlowchartWidget(QWidget* parent);

    /**
     * @brief Initialize a new flowchart
     *
     * @param practice_structure
     */
    void initialize_flowchart(std::shared_ptr<PracticeStructure> practice_structure);

private:
    /**
     * @brief Add the widget corresponding to the latest step
     */
    void add_step_widget();

    /**
     * @brief Remove the widget corresponding to a given step
     *
     * @param step_index index of step to remove
     */
    void remove_step_widget(unsigned int step_index);

public slots:
    /**
     * @brief Handle a user answer
     *
     * @param step_index index of answered step
     * @param answer
     */
    void handle_answer(int step_index, int answer);

private slots:
    /**
     * @brief Scroll the widget to the bottom
     */
    void scroll_to_bottom();

signals:
    /**
     * @brief Emitted when the user has finished the exercise
     */
    void finished_exercise();
};

#endif  // GUI_PRACTICE_FLOWCHART_WIDGET_H
