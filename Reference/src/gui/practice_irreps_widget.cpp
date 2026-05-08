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

#include "practice_irreps_widget.h"

/**
 * @brief Construct a new PracticeIrrepsWidget object
 *
 * @param parent pointer to parent widget
 */
PracticeIrrepsWidget::PracticeIrrepsWidget(QWidget* parent) {
    this->container = new QWidget;
    this->layout = new QVBoxLayout;
    this->setWidget(container);
    this->setWidgetResizable(true);
    this->container->setLayout(this->layout);

    connect(this->verticalScrollBar(), SIGNAL(rangeChanged(int, int)), this, SLOT(scroll_to_bottom()));

    this->part1 = new QWidget;
    this->part1->setVisible(false);
    QVBoxLayout *part1_layout = new QVBoxLayout;
    part1_layout->setContentsMargins(0, 0, 0, 0);
    this->part1->setLayout(part1_layout);
    this->layout->addWidget(this->part1);

    this->q1 = new QLabel;
    this->q1->setText("Consider the <b>xxx</b> atomic orbitals of <b>xxx</b> (the highlighted atoms) as basis set. How many orbitals remain in place for each symmetry operation? (Take the direction of the orbital into account!)");
    this->q1->setTextFormat(Qt::TextFormat::RichText);
    this->q1->setWordWrap(true);
    part1_layout->addWidget(this->q1);

    this->operation_characters_grid = new QGridLayout;
    part1_layout->addLayout(this->operation_characters_grid);

    this->submit_operation_characters = new QPushButton;
    this->submit_operation_characters->setText("Continue");
    part1_layout->addWidget(this->submit_operation_characters);
    connect(this->submit_operation_characters, SIGNAL(clicked()), this, SLOT(show_part2()));

    this->part2 = new QWidget;
    this->part2->setVisible(false);
    QVBoxLayout *part2_layout = new QVBoxLayout;
    part2_layout->setContentsMargins(0, 0, 0, 0);
    this->part2->setLayout(part2_layout);
    this->layout->addWidget(this->part2);

    QLabel *q2 = new QLabel;
    q2->setText("Now, apply the little orthogonality theorem on the results you obtained and determine to which irreducible representations this basis set belongs.");
    q2->setWordWrap(true);
    part2_layout->addWidget(q2);

    QPushButton *open_character_table = new QPushButton;
    open_character_table->setText("View character table");
    part2_layout->addWidget(open_character_table);
    connect(open_character_table, SIGNAL(clicked()), parent, SIGNAL(open_character_table_dialog()));

    this->irrep_coefficients_grid = new QGridLayout;
    part2_layout->addLayout(this->irrep_coefficients_grid);

    this->irrep_sum = new QLabel;
    this->irrep_sum->setText("Γ = …");
    this->irrep_sum->setWordWrap(true);
    part2_layout->addWidget(this->irrep_sum);

    this->submit_irrep_coefficients = new QPushButton;
    this->submit_irrep_coefficients->setText("Show answers");
    part2_layout->addWidget(this->submit_irrep_coefficients);
    connect(this->submit_irrep_coefficients, SIGNAL(clicked()), this, SLOT(show_answers()));

    this->layout->addStretch();
}

/**
 * @brief Initialize a new exercise
 *
 * @param practice_structure
 */
void PracticeIrrepsWidget::initialize(std::shared_ptr<PracticeStructure> practice_structure) {
    this->irreps = PracticeIrreps(practice_structure);

    this->submit_operation_characters->setVisible(true);
    this->part2->setVisible(false);

    this->q1->setText(QString("Consider the <b>%1</b> atomic orbitals of <b>%2</b> (the highlighted atoms) as basis set. How many orbitals remain in place for each symmetry operation?")
        .arg(QString::fromStdString(practice_structure->get_basis_set()->get_orbital_label().get_name_html()))
        .arg(QString::fromStdString(practice_structure->get_basis_set()->get_element().name)));

    while (this->operation_characters_grid->count() > 0) {
        delete this->operation_characters_grid->itemAt(0)->widget();
    }
    while (this->irrep_coefficients_grid->count() > 0) {
        delete this->irrep_coefficients_grid->itemAt(0)->widget();
    }

    // build grids
    auto correct_characters = this->irreps.get_correct_characters();

    // manually add identity
    QLabel* identity_label = new QLabel;
    identity_label->setText("<i>E</i>");
    identity_label->setTextFormat(Qt::TextFormat::RichText);
    this->operation_characters_grid->addWidget(identity_label, 0, 0, Qt::AlignmentFlag::AlignRight);

    QLineEdit* identity_character = new QLineEdit;
    identity_character->setText(QString::number(practice_structure->get_basis_set()->get_atoms().size()));
    identity_character->setEnabled(false);
    this->operation_characters_grid->addWidget(identity_character, 0, 1);

    for (unsigned int i = 0; i < correct_characters.size(); ++i) {
        QLabel *operation_label = new QLabel;
        operation_label->setText(QString::fromStdString(correct_characters[i].first.get_short_name_html()));
        operation_label->setTextFormat(Qt::TextFormat::RichText);
        this->operation_characters_grid->addWidget(operation_label, i + 1, 0, Qt::AlignmentFlag::AlignRight);

        QLineEdit *character_input = new QLineEdit;
        QDoubleValidator *validator = new QDoubleValidator;
        character_input->setPlaceholderText("0");
        character_input->setValidator(validator);
        this->operation_characters_grid->addWidget(character_input, i + 1, 1);

        QLabel *correct_character_label = new QLabel;
        correct_character_label->setVisible(false);
        this->operation_characters_grid->addWidget(correct_character_label, i + 1, 2);
    }

    auto correct_irreps = this->irreps.get_correct_irreps();
    for (unsigned int i = 0; i < correct_irreps.size(); ++i) {
        QLabel *irrep_label = new QLabel;
        irrep_label->setText(QString::fromStdString(correct_irreps[i].first.get_name_html()));
        irrep_label->setTextFormat(Qt::TextFormat::RichText);
        this->irrep_coefficients_grid->addWidget(irrep_label, i, 0, Qt::AlignmentFlag::AlignRight);

        QLineEdit *coefficient_input = new QLineEdit;
        QDoubleValidator *validator = new QDoubleValidator;
        coefficient_input->setPlaceholderText("0");
        coefficient_input->setValidator(validator);
        this->irrep_coefficients_grid->addWidget(coefficient_input, i, 1);
        connect(coefficient_input, SIGNAL(textEdited(QString)), this, SLOT(update_irrep_sum()));

        QLabel *correct_coefficient_label = new QLabel;
        correct_coefficient_label->setVisible(false);
        this->irrep_coefficients_grid->addWidget(correct_coefficient_label, i, 2);
    }

    this->part1->setVisible(true);

    // highlight basis set atoms
    const std::vector<unsigned int>& basis_set_atoms = practice_structure->get_basis_set()->get_atoms();
    QList<unsigned int> basis_set_atoms_list;
    basis_set_atoms_list.reserve(basis_set_atoms.size());
    std::copy(basis_set_atoms.begin(), basis_set_atoms.end(), std::back_inserter(basis_set_atoms_list));

    emit this->highlight_atoms(basis_set_atoms_list);
}

/**
 * @brief Scroll the widget to the bottom
 */
void PracticeIrrepsWidget::scroll_to_bottom() {
    this->verticalScrollBar()->setValue(this->verticalScrollBar()->maximum());
}

/**
 * @brief Show the second part of the exercise
 */
void PracticeIrrepsWidget::show_part2() {
    this->submit_operation_characters->setVisible(false);
    this->part2->setVisible(true);
}

/**
 * @brief Show the correct answers
 */
void PracticeIrrepsWidget::show_answers() {
    auto correct_characters = this->irreps.get_correct_characters();
    for (unsigned int i = 0; i < correct_characters.size(); ++i) {
        // skip identity
        QLineEdit *line_edit = static_cast<QLineEdit*>(this->operation_characters_grid->itemAtPosition(i + 1, 1)->widget());
        QLabel *label = static_cast<QLabel*>(this->operation_characters_grid->itemAtPosition(i + 1, 2)->widget());

        int input = line_edit->text().toInt();
        if (input == correct_characters[i].second) {
            label->setText("Correct!");
        } else {
            label->setText(QString("Incorrect (%1)").arg(correct_characters[i].second));
        }
        label->setVisible(true);
    }

    auto correct_irreps = this->irreps.get_correct_irreps();
    for (unsigned int i = 0; i < correct_irreps.size(); ++i) {
        QLineEdit *line_edit = static_cast<QLineEdit*>(this->irrep_coefficients_grid->itemAtPosition(i, 1)->widget());
        QLabel *label = static_cast<QLabel*>(this->irrep_coefficients_grid->itemAtPosition(i, 2)->widget());

        int input = line_edit->text().toInt();
        if (input == correct_irreps[i].second) {
            label->setText("Correct!");
        } else {
            label->setText(QString("Incorrect (%1)").arg(correct_irreps[i].second));
        }
        label->setVisible(true);
    }

    emit finished_exercise();
}

/**
 * @brief Update the label showing the sum of the irreps
 */
void PracticeIrrepsWidget::update_irrep_sum() {
    auto irreps = this->irreps.get_correct_irreps();

    std::vector<std::string> parts;
    for (unsigned int i = 0; i < irreps.size(); ++i) {
        QLineEdit *line_edit = static_cast<QLineEdit*>(this->irrep_coefficients_grid->itemAtPosition(i, 1)->widget());
        int input = line_edit->text().toInt();

        if (input != 0) {
            parts.push_back(((input != 1) ? std::to_string(input) + " " : "") + irreps[i].first.get_name_html());
        }
    }

    if (parts.size() == 0) {
        this->irrep_sum->setText("Γ = …");
    } else {
        this->irrep_sum->setText(QString::fromStdString("Γ = " + boost::join(parts, " \u2295 ")));
    }
}
