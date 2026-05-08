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

#include "practice_config_widget.h"

/**
 * @brief Construct a new PracticeConfigWidget object
 *
 * @param parent pointer to parent widget
 */
PracticeConfigWidget::PracticeConfigWidget(QWidget* parent) {
    this->container = new QWidget;
    this->layout = new QVBoxLayout;
    this->setWidget(container);
    this->setWidgetResizable(true);
    this->container->setLayout(this->layout);

    QLabel *label = new QLabel;
    label->setText("Types of practice exercises:");
    this->layout->addWidget(label);

    this->flowchart_checkbox = new QCheckBox;
    this->flowchart_checkbox->setText("Point group determination");
    this->flowchart_checkbox->setChecked(true);
    this->layout->addWidget(this->flowchart_checkbox);

    this->irreps_checkbox = new QCheckBox;
    this->irreps_checkbox->setText("Irreducible representation");
    this->irreps_checkbox->setChecked(true);
    this->layout->addWidget(this->irreps_checkbox);

    this->projection_checkbox = new QCheckBox;
    this->projection_checkbox->setText("Projection operator");
    this->projection_checkbox->setChecked(true);
    this->layout->addWidget(this->projection_checkbox);

    this->start_button = new QPushButton;
    this->start_button->setText("Start practice");
    this->layout->addWidget(this->start_button);
    connect(this->start_button, SIGNAL(clicked()), this, SLOT(create_practice_config()));

    layout->addStretch();
}

/**
 * @brief Get the practice configuration object
 *
 * @return std::shared_ptr<PracticeConfig>
 */
std::shared_ptr<PracticeConfig>& PracticeConfigWidget::get_practice_config() {
    return this->practice_config;
}

/**
 * @brief Create the configuration object based on the user's input
 */
void PracticeConfigWidget::create_practice_config() {
    this->practice_config = std::make_shared<PracticeConfig>();

    if (this->flowchart_checkbox->isChecked()) this->practice_config->add_module(PracticeModule::Flowchart);
    if (this->irreps_checkbox->isChecked()) this->practice_config->add_module(PracticeModule::Irreps);
    if (this->projection_checkbox->isChecked()) this->practice_config->add_module(PracticeModule::Projection);

    if (this->practice_config->get_enabled_modules().size() > 0) emit start();
}
