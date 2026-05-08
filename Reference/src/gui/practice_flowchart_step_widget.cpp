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

#include "practice_flowchart_step_widget.h"

/**
 * @brief Construct a new Practice Flowchart Step Widget object
 *
 * @param step step to build widget from
 */
PracticeFlowchartStepWidget::PracticeFlowchartStepWidget(QWidget* parent, int step_index, std::shared_ptr<PracticeFlowchartStep> step) {
    this->parent = parent;
    this->step_index = step_index;
    this->step = step;
    this->build_widget();
}

/**
 * @brief Generate and show correct answer
 */
void PracticeFlowchartStepWidget::show_answer() {
    if (this->step->get_type() != PracticeFlowchartStep::Type::Result) {
        if (this->step->get_correct_answer() == this->answer) {
            answer_label->setText("Correct!");
        } else {
            if (this->step->get_type() == PracticeFlowchartStep::Type::ChooseN) {
                answer_label->setText(QString("Incorrect; the correct answer is %1.").arg(this->step->get_correct_answer()));
            } else {
                answer_label->setText("Incorrect.");
            }
        }
    } else {
        PointGroupLabel correct_group = this->step->get_correct_point_group();
        PointGroupLabel result_group = this->step->get_result_point_group();

        if (correct_group.matches(result_group)) {
            answer_label->setText("Correct!");
        } else {
            answer_label->setText(QString("Incorrect; the correct answer is %1.").arg(QString::fromStdString(correct_group.get_name_html())));
        }
    }

    this->set_answer_visible(true);
}

/**
 * @brief Set the visibility of the answer
 *
 * @param answer_visible
 */
void PracticeFlowchartStepWidget::set_answer_visible(bool answer_visible) {
    this->answer_label->setVisible(answer_visible);
}

/**
 * @brief Build the widget
 */
void PracticeFlowchartStepWidget::build_widget() {
    if (this->widget_built) return;

    this->main_layout = new QVBoxLayout;

    QLabel *text_label = new QLabel;
    text_label->setWordWrap(true);
    text_label->setTextFormat(Qt::TextFormat::RichText);
    text_label->setText(QString::fromStdString(this->step->get_text()));
    this->main_layout->addWidget(text_label);

    this->input_layout = new QHBoxLayout;
    this->main_layout->addLayout(this->input_layout);

    this->answer_label = new QLabel;
    this->answer_label->setWordWrap(true);
    this->answer_label->setTextFormat(Qt::TextFormat::RichText);
    this->answer_label->setVisible(false);
    this->main_layout->addWidget(answer_label);

    if (this->step->get_type() == PracticeFlowchartStep::Type::NoYes) {
        QSignalMapper *signal_mapper = new QSignalMapper;

        QPushButton *yes_button = new QPushButton;
        yes_button->setCheckable(true);
        yes_button->setText("Yes");
        this->input_layout->addWidget(yes_button);
        signal_mapper->setMapping(yes_button, 1);
        connect(yes_button, SIGNAL(released()), signal_mapper, SLOT(map()));

        QPushButton *no_button = new QPushButton;
        no_button->setCheckable(true);
        no_button->setText("No");
        this->input_layout->addWidget(no_button);
        signal_mapper->setMapping(no_button, 0);
        connect(no_button, SIGNAL(released()), signal_mapper, SLOT(map()));

        QButtonGroup *button_group = new QButtonGroup;
        button_group->setExclusive(true);
        button_group->addButton(yes_button);
        button_group->addButton(no_button);

        connect(signal_mapper, SIGNAL(mapped(int)), this, SLOT(handle_no_yes_answer(int)));
    } else if (this->step->get_type() == PracticeFlowchartStep::Type::ChooseN) {
        this->combobox = new QComboBox;
        for (int i = 2; i <= 10; ++i) {
            this->combobox->addItem(QString::number(i), i);
        }
        this->input_layout->addWidget(this->combobox);

        QPushButton *select_button = new QPushButton;
        select_button->setText("Select");
        this->input_layout->addWidget(select_button);
        connect(select_button, SIGNAL(released()), this, SLOT(handle_choose_answer()));
    } else if (this->step->get_type() == PracticeFlowchartStep::Type::Result) {
        QPushButton *check_button = new QPushButton;
        check_button->setText("Check answers");
        this->input_layout->addWidget(check_button);
        connect(check_button, SIGNAL(released()), this, SLOT(handle_check_answer()));
    }

    this->setLayout(this->main_layout);

    connect(this, SIGNAL(submit_answer(int, int)), this->parent, SLOT(handle_answer(int, int)));
}

/**
 * @brief Clean the widget
 */
void PracticeFlowchartStepWidget::clean_widget() {
    for (auto child : this->input_layout->findChildren<QWidget*>("", Qt::FindDirectChildrenOnly)) {
        delete child;
    }
    for (auto child : this->main_layout->findChildren<QWidget*>("", Qt::FindDirectChildrenOnly)) {
        delete child;
    }
    delete this->main_layout;
}

/**
 * @brief Handle an answer to a No/Yes step
 *
 * @param answer
 */
void PracticeFlowchartStepWidget::handle_no_yes_answer(int answer) {
    this->answer = answer;
    emit this->submit_answer(this->step_index, this->answer);
}

/**
 * @brief Handle an answer to a choose step
 */
void PracticeFlowchartStepWidget::handle_choose_answer() {
    this->answer = this->combobox->currentData().toInt();
    emit this->submit_answer(this->step_index, this->answer);
}

/**
 * @brief Handle clicking the "check answers" button
 */
void PracticeFlowchartStepWidget::handle_check_answer() {
    emit this->submit_answer(this->step_index, -1);
}
