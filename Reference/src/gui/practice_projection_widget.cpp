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

#include "practice_projection_widget.h"

/**
 * @brief Construct a new PracticeProjectionWidget object
 *
 * @param parent pointer to parent widget
 */
PracticeProjectionWidget::PracticeProjectionWidget(QWidget* parent) {
    this->container = new QWidget;
    this->layout = new QVBoxLayout;
    this->setWidget(container);
    this->setWidgetResizable(true);
    this->container->setLayout(this->layout);

    connect(this->verticalScrollBar(), SIGNAL(rangeChanged(int, int)), this, SLOT(scroll_to_bottom()));

    this->question = new QLabel;
    this->question->setText("Apply the projection operator to the <b>xxx</b> atomic orbital of the atom labelled <b>xxx</b>. How does this orbital transform under each symmetry operation of the point group?");
    this->question->setTextFormat(Qt::TextFormat::RichText);
    this->question->setWordWrap(true);
    this->layout->addWidget(this->question);

    QWidget *grid_container = new QWidget;
    this->grid_layout = new QVBoxLayout;
    this->grid_layout->setContentsMargins(0, 0, 0, 0);
    this->layout->addWidget(grid_container);
    grid_container->setLayout(this->grid_layout);

    this->button_group = new QButtonGroup;
    connect(this->button_group, SIGNAL(idClicked(int)), this, SLOT(show_next(int)));

    this->layout->addStretch();
}

/**
 * @brief Initialize a new exercise
 *
 * @param practice_structure
 */
void PracticeProjectionWidget::initialize(std::shared_ptr<PracticeStructure> practice_structure) {
    this->projection = PracticeProjection(practice_structure);

    this->question->setText(QString("Apply the projection operator to the <b>%1</b> atomic orbital of the atom labelled <b>%2</b>. How does this orbital transform under each symmetry operation of the point group?")
        .arg(QString::fromStdString(practice_structure->get_basis_set()->get_orbital_label().get_name_html()))
        .arg(practice_structure->get_base_atom() + 1));

    for (QGridLayout* grid : this->grids) {
        while (grid->count() > 0) {
            delete grid->itemAt(0)->widget();
        }
        delete grid;
    }
    for (QWidget* grid_container : this->grid_containers) {
        delete grid_container;
    }
    for (QPushButton* button : this->buttons) {
        this->button_group->removeButton(button);
        delete button;
    }
    this->grid_containers.clear();
    this->grids.clear();
    this->buttons.clear();

    // build grids
    auto correct_coefficients = this->projection.get_correct_coefficients();

    // manually add identity
    this->grid_containers.push_back(new QWidget);
    this->grids.push_back(new QGridLayout);
    this->grids[0]->setContentsMargins(0, 0, 0, 0);
    this->grid_containers[0]->setLayout(this->grids[0]);

    QLabel* identity_label = new QLabel;
    identity_label->setText("<i>E</i> identity");
    identity_label->setTextFormat(Qt::TextFormat::RichText);
    this->grids[0]->addWidget(identity_label, 0, 0, 1, 3);

    for (unsigned int j = 0; j < practice_structure->get_basis_set()->get_atoms().size(); ++j) {
        QLabel *orbital_label = new QLabel;
        orbital_label->setText(QString::number(j + 1));
        this->grids[0]->addWidget(orbital_label, j + 1, 0, Qt::AlignmentFlag::AlignRight);

        QLineEdit *coefficient = new QLineEdit;
        coefficient->setText((j == practice_structure->get_base_atom()) ? "1" : "0");
        coefficient->setEnabled(false);
        this->grids[0]->addWidget(coefficient, j + 1, 1);
    }

    this->grid_layout->addWidget(this->grid_containers[0]);

    this->buttons.push_back(new QPushButton);
    this->buttons[0]->setText("Continue");
    this->button_group->addButton(this->buttons[0], 0);
    this->grid_layout->addWidget(this->buttons[0]);

    for (unsigned int i = 0; i < correct_coefficients.size(); ++i) {
        this->grid_containers.push_back(new QWidget);
        this->grids.push_back(new QGridLayout);
        this->grids[i + 1]->setContentsMargins(0, 0, 0, 0);
        this->grid_containers[i + 1]->setVisible(false);
        this->grid_containers[i + 1]->setLayout(this->grids[i + 1]);

        QLabel* operation_label = new QLabel;
        operation_label->setText(QString::fromStdString(correct_coefficients[i].first.get_name_html()));
        operation_label->setTextFormat(Qt::TextFormat::RichText);
        this->grids[i + 1]->addWidget(operation_label, 0, 0, 1, 3);

        for (unsigned int j = 0; j < practice_structure->get_basis_set()->get_atoms().size(); ++j) {
            QLabel *orbital_label = new QLabel;
            orbital_label->setText(QString::number(j + 1));
            this->grids[i + 1]->addWidget(orbital_label, j + 1, 0, Qt::AlignmentFlag::AlignRight);

            QLineEdit *coefficient_input = new QLineEdit;
            QDoubleValidator *validator = new QDoubleValidator;
            coefficient_input->setPlaceholderText("0");
            coefficient_input->setValidator(validator);
            this->grids[i + 1]->addWidget(coefficient_input, j + 1, 1);

            QLabel *correct_coefficient_label = new QLabel;
            correct_coefficient_label->setVisible(false);
            this->grids[i + 1]->addWidget(correct_coefficient_label, j + 1, 2);
        }

        this->grid_layout->addWidget(this->grid_containers[i + 1]);

        this->buttons.push_back(new QPushButton);
        this->buttons[i + 1]->setText((i == correct_coefficients.size() - 1) ? "Show answers" : "Continue");
        this->buttons[i + 1]->setVisible(false);
        this->button_group->addButton(this->buttons[i + 1], i + 1);
        this->grid_layout->addWidget(this->buttons[i + 1]);
    }

    // highlight 'basis' atom
    // note that the base atom index is with respect to the basis set
    unsigned int highlight_idx = practice_structure->get_basis_set()->get_atoms()[practice_structure->get_base_atom()];
    emit this->highlight_atoms({highlight_idx});

    // label basis set atoms
    const std::vector<unsigned int>& basis_set_atoms = practice_structure->get_basis_set()->get_atoms();
    QMap<unsigned int, std::string> labels;
    for (unsigned int i = 0; i < basis_set_atoms.size(); ++i) {
        labels.insert(basis_set_atoms[i], std::to_string(i + 1));
    }

    emit this->label_atoms(labels);
}

/**
 * @brief Show the correct answers
 */
void PracticeProjectionWidget::show_answers() {
    auto correct_coefficients = this->projection.get_correct_coefficients();
    for (unsigned int i = 0; i < correct_coefficients.size(); ++i) {
        // skip identity
        auto operation_correct = correct_coefficients[i].second;
        for (unsigned int j = 0; j < operation_correct.size(); ++j) {
            QLineEdit *line_edit = static_cast<QLineEdit*>(this->grids[i + 1]->itemAtPosition(j + 1, 1)->widget());
            QLabel *label = static_cast<QLabel*>(this->grids[i + 1]->itemAtPosition(j + 1, 2)->widget());

            double input = line_edit->text().toDouble();
            if ((input - operation_correct[j] < 1e-2) && (operation_correct[j] - input < 1e-2)) {
                label->setText("Correct!");
            } else {
                label->setText(QString("Incorrect (%1)").arg(operation_correct[j]));
            }
            label->setVisible(true);
        }
    }

    emit finished_exercise();
}

/**
 * @brief Scroll the widget to the bottom
 */
void PracticeProjectionWidget::scroll_to_bottom() {
    this->verticalScrollBar()->setValue(this->verticalScrollBar()->maximum());
}

/**
 * @brief Show the next part of the exercise
 *
 * @param id button id
 */
void PracticeProjectionWidget::show_next(int id) {
    if (id < this->projection.get_correct_coefficients().size()) {
        this->buttons[id]->setVisible(false);
        this->grid_containers[id + 1]->setVisible(true);
        this->buttons[id + 1]->setVisible(true);
    } else {
        this->show_answers();
    }
}
