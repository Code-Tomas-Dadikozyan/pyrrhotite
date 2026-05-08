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

#ifndef GUI_PRACTICE_FLOWCHART_STEP_WIDGET_H
#define GUI_PRACTICE_FLOWCHART_STEP_WIDGET_H

#include <memory>
#include <Qt>
#include <QButtonGroup>
#include <QComboBox>
#include <QFrame>
#include <QHBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QSignalMapper>
#include <QString>
#include <QVBoxLayout>
#include <QWidget>
#include "../practice/practice_flowchart_step.h"

class PracticeFlowchartStepWidget: public QWidget {
    Q_OBJECT

private:
    QWidget* parent;
    std::shared_ptr<PracticeFlowchartStep> step;

    int step_index;
    int answer;

    bool widget_built = false;
    QVBoxLayout* main_layout;
    QHBoxLayout* input_layout;

    QComboBox* combobox;
    QLabel *answer_label;

public:
    /**
     * @brief Construct a new Practice Flowchart Step Widget object
     *
     * @param step step to build widget from
     */
    PracticeFlowchartStepWidget(QWidget* parent, int step_index, std::shared_ptr<PracticeFlowchartStep> step);

    /**
     * @brief Generate and show correct answer
     */
    void show_answer();

    /**
     * @brief Set the visibility of the answer
     *
     * @param answer_visible
     */
    void set_answer_visible(bool answer_visible);

private:
    /**
     * @brief Build the widget
     */
    void build_widget();

public:
    /**
     * @brief Clean the widget
     */
    void clean_widget();

private slots:
    /**
     * @brief Handle an answer to a No/Yes step
     *
     * @param answer
     */
    void handle_no_yes_answer(int answer);

    /**
     * @brief Handle an answer to a choose step
     */
    void handle_choose_answer();

    /**
     * @brief Handle clicking the "check answers" button
     */
    void handle_check_answer();

signals:
    /**
     * @brief Submit the answer to the flowchart widget
     *
     * @param step_index
     * @param answer
     */
    void submit_answer(int step_index, int answer);
};

#endif  // GUI_PRACTICE_FLOWCHART_STEP_WIDGET_H
