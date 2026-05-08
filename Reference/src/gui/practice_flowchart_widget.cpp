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

#include "practice_flowchart_widget.h"

/**
 * @brief Construct a new PracticeFlowchartWidget object
 *
 * @param parent pointer to parent widget
 */
PracticeFlowchartWidget::PracticeFlowchartWidget(QWidget* parent) {
    this->container = new QWidget;
    this->layout = new QVBoxLayout;
    this->layout->setContentsMargins(0, 0, 0, 0);
    this->setWidget(container);
    this->setWidgetResizable(true);
    this->container->setLayout(this->layout);

    connect(this->verticalScrollBar(), SIGNAL(rangeChanged(int, int)), this, SLOT(scroll_to_bottom()));

    layout->addStretch();
}

/**
 * @brief Initialize a new flowchart object
 *
 * @param practice_structure
 */
void PracticeFlowchartWidget::initialize_flowchart(std::shared_ptr<PracticeStructure> practice_structure) {
    // remove all existing step widgets
    for (int i = this->step_widgets.size() - 1; i >= 0; --i) {
        this->remove_step_widget(i);
    }

    this->flowchart = PracticeFlowchart(practice_structure);
    this->add_step_widget();
}

/**
 * @brief Add the widget corresponding to the latest step
 */
void PracticeFlowchartWidget::add_step_widget() {
    unsigned int step_index = this->flowchart.get_latest_step_index();
    this->step_widgets.push_back(new PracticeFlowchartStepWidget(this, step_index, this->flowchart.get_step(step_index)));
    this->layout->insertWidget(step_index, this->step_widgets[step_index]);
}

/**
 * @brief Remove the widget corresponding to a given step
 *
 * @param step_index index of step to remove
 */
void PracticeFlowchartWidget::remove_step_widget(unsigned int step_index) {
    this->layout->removeWidget(this->step_widgets[step_index]);
    this->step_widgets[step_index]->setVisible(false);
    this->step_widgets[step_index]->clean_widget();
    this->step_widgets.erase(this->step_widgets.begin() + step_index);
}

/**
 * @brief Handle a user answer
 *
 * @param step_index index of answered step
 * @param answer
 */
void PracticeFlowchartWidget::handle_answer(int step_index, int answer) {
    if (this->flowchart.handle_answer(step_index, answer)) {
        // clear steps after this step
        for (int i = this->step_widgets.size() - 1; i > step_index; --i) {
            this->remove_step_widget(i);
        }

        this->add_step_widget();
    }

    if (answer == -1) {
        // check answers
        for (auto step_widget : this->step_widgets) {
            step_widget->show_answer();
        }
        emit finished_exercise();
    } else {
        // reset answer visibility
        for (auto step_widget : this->step_widgets) {
            step_widget->set_answer_visible(false);
        }
    }
}

/**
 * @brief Scroll the widget to the bottom
 */
void PracticeFlowchartWidget::scroll_to_bottom() {
    this->verticalScrollBar()->setValue(this->verticalScrollBar()->maximum());
}
