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

#include "character_table_dialog.h"

/**
 * @brief Construct a new Character Table Dialog object
 *
 * @param parent
 */
CharacterTableDialog::CharacterTableDialog(QWidget* parent)
    : QDialog(parent, Qt::WindowType::WindowTitleHint |
                      Qt::WindowType::WindowSystemMenuHint |
                      Qt::WindowCloseButtonHint) {
    this->setWindowTitle("Character tables");
    this->setWindowModality(Qt::WindowModality::NonModal);

    QHBoxLayout *layout = new QHBoxLayout;
    this->setLayout(layout);

    this->point_group_view = new QTreeView;
    this->point_group_model = new QStandardItemModel;
    PointGroupItemDelegate *point_group_delegate = new PointGroupItemDelegate;
    this->populate_point_groups();

    this->point_group_view->setFixedWidth(120);
    this->point_group_view->setMinimumHeight(200);
    this->point_group_view->setEditTriggers(QTreeView::EditTrigger::NoEditTriggers);
    this->point_group_view->setHeaderHidden(true);
    this->point_group_view->setIndentation(0);
    this->point_group_view->setItemsExpandable(false);
    this->point_group_view->setSizePolicy(QSizePolicy::Policy::Minimum, QSizePolicy::Policy::MinimumExpanding);
    this->point_group_view->setModel(this->point_group_model);
    this->point_group_view->setItemDelegate(point_group_delegate);

    QItemSelectionModel *selection_model = this->point_group_view->selectionModel();

    connect(selection_model, SIGNAL(selectionChanged(const QItemSelection&, const QItemSelection&)), this, SLOT(select_point_group(const QItemSelection&)));

    layout->addWidget(this->point_group_view);

    this->character_table_view = new QTableView;
    this->character_table_model = new QStandardItemModel;
    CharacterTableItemDelegate *character_table_delegate = new CharacterTableItemDelegate;
    RichTextHeaderView *horizontal_header = new RichTextHeaderView(Qt::Orientation::Horizontal);
    RichTextHeaderView *vertical_header = new RichTextHeaderView(Qt::Orientation::Vertical);
    horizontal_header->setDefaultSectionSize(70);
    horizontal_header->setSectionResizeMode(QHeaderView::ResizeMode::Fixed);
    vertical_header->setDefaultSectionSize(24);
    vertical_header->setSectionResizeMode(QHeaderView::ResizeMode::Fixed);

    this->character_table_view->setSizePolicy(QSizePolicy::Policy::MinimumExpanding, QSizePolicy::Policy::Minimum);
    this->character_table_view->setModel(this->character_table_model);
    this->character_table_view->setItemDelegate(character_table_delegate);
    this->character_table_view->setHorizontalHeader(horizontal_header);
    this->character_table_view->setVerticalHeader(vertical_header);

    layout->addWidget(this->character_table_view);
}

/**
 * @brief Show the point group given by the point group label
 *
 * @param label
 */
void CharacterTableDialog::show_point_group(PointGroupLabel label) {
    std::vector<PointGroup> point_groups = PointGroups::point_groups;

    for (unsigned int i = 0; i < point_groups.size(); ++i) {
        if (point_groups[i].get_label().matches(label)) {
            this->update_point_group_selection(i);
            this->show_point_group(i);
            return;
        }
    }

    throw std::runtime_error("Point group not found.");
}

/**
 * @brief Show the point group given by the index
 *
 * @param index
 */
void CharacterTableDialog::show_point_group(unsigned int index) {
    this->character_table_model->clear();

    PointGroup point_group = PointGroups::point_groups[index];

    if (!point_group.get_label().is_linear()) {
        this->populate_character_table(point_group);
    } else {
        this->populate_character_table_linear(point_group);
    }

    // resize
    int w = this->character_table_view->verticalHeader()->width() + 2;
    for (unsigned int j = 0; j < this->character_table_model->columnCount(); ++j) {
        w += this->character_table_view->columnWidth(j);
    }
    int h = this->character_table_view->horizontalHeader()->height() + 2;
    for (unsigned int i = 0; i < this->character_table_model->rowCount(); ++i) {
        h += this->character_table_view->rowHeight(i);
    }

    this->character_table_view->setMinimumSize(w, h);
    this->adjustSize();
}

/**
 * @brief Add items to the point group model
 */
void CharacterTableDialog::populate_point_groups() {
    this->point_group_model->clear();

    std::vector<PointGroup> point_groups = PointGroups::point_groups;

    for (unsigned int i = 0; i < point_groups.size(); ++i) {
        QStandardItem* model_item = new QStandardItem(QString("<span>%1</span>").arg(
            QString::fromStdString(point_groups[i].get_label().get_name_html())));
        model_item->setData(i, PointGroupItemDelegate::ItemDataRole::IndexRole);

        this->point_group_model->appendRow(model_item);
    }
}

/**
 * @brief Add items to the character table model
 *
 * @param point_group point group to add items from
 */
void CharacterTableDialog::populate_character_table(PointGroup& point_group) {
    std::vector<IrrepLabel> irreps = point_group.get_irreps();
    for (unsigned int i = 0; i < irreps.size(); ++i) {
        QStandardItem* item = new QStandardItem(QString("<span>%1</span>").arg(
            QString::fromStdString(irreps[i].get_name_html())));
        this->character_table_model->setVerticalHeaderItem(i, item);
    }

    std::vector<OperationLabelCount> operations = point_group.get_unique_operations();
    // manually add identity
    QStandardItem *identity_item = new QStandardItem("<span><i>E</i></span>");
    this->character_table_model->setHorizontalHeaderItem(0, identity_item);
    for (unsigned int j = 0; j < operations.size(); ++j) {
        QStandardItem *item = new QStandardItem(QString("<span>%1</span>").arg(
            QString::fromStdString(operations[j].get_short_name_html())));
        this->character_table_model->setHorizontalHeaderItem(j + 1, item);
    }

    std::vector<std::vector<double>> characters = point_group.get_characters();
    for (unsigned int i = 0; i < irreps.size(); ++i) {
        for (unsigned int j = 0; j < operations.size() + 1; ++j) {
            QStandardItem *item = new QStandardItem(this->format_number(characters[i][j]));
            item->setFlags(Qt::ItemFlag::NoItemFlags);
            item->setTextAlignment(Qt::AlignmentFlag::AlignCenter);
            this->character_table_model->setItem(i, j, item);
        }
    }
}

/**
 * @brief Add items to the character table model from a linear point group
 * (Cinfv or Dinfh)
 *
 * These items are added manually due to the infinite number of characters;
 * they do not fit in the existing framework.
 *
 * @param point_group
 */
void CharacterTableDialog::populate_character_table_linear(PointGroup& point_group) {
    switch (point_group.get_label().get_class()) {
        case PointGroupLabel::Class::Cinfv:
            this->populate_character_table_Cinfv();
            break;
        case PointGroupLabel::Class::Dinfh:
            this->populate_character_table_Dinfh();
            break;
        default:
            throw std::runtime_error("Unexpected point group class encountered.");
    }
}

/**
 * @brief Add items to the character table model for the Cinfv point group
 */
void CharacterTableDialog::populate_character_table_Cinfv() {
    this->character_table_model->setVerticalHeaderLabels({
        "A<sub>1</sub> = Σ<sup>+</sup>",
        "A<sub>2</sub> = Σ<sup>\u2212</sup>",
        "E<sub>1</sub> = Π",
        "E<sub>2</sub> = Δ",
        "E<sub>3</sub> = Φ",
        "\u22ee",
        "E<sub><i>n</i></sub>"
    });

    this->character_table_model->setHorizontalHeaderLabels({
        "E",
        "2 <i>C</i><sub>∞</sub>",
        "\u22ef",
        "∞ <i>σ</i><sub>v</sub>"
    });

    const std::vector<std::vector<QString>> characters = {
        {"1", "1", "\u22ef", "1"},
        {"1", "1", "\u22ef", "\u22121"},
        {"2", "2 cos(φ)", "\u22ef", "0"},
        {"2", "2 cos(2φ)", "\u22ef", "0"},
        {"2", "2 cos(3φ)", "\u22ef", "0"},
        {"\u22ee", "\u22ee", "\u22f1", "\u22ee"},
        {"2", "2 cos(<i>n</i>φ)", "\u22ef", "0"}
    };
    for (unsigned int i = 0; i < characters.size(); ++i) {
        for (unsigned int j = 0; j < characters[i].size(); ++j) {
            QStandardItem *item = new QStandardItem(characters[i][j]);
            item->setFlags(Qt::ItemFlag::NoItemFlags);
            item->setTextAlignment(Qt::AlignmentFlag::AlignCenter);
            this->character_table_model->setItem(i, j, item);
        }
    }
}

/**
 * @brief Add items to the character table model for the Dinfh point group
 */
void CharacterTableDialog::populate_character_table_Dinfh() {
    this->character_table_model->setVerticalHeaderLabels({
        "A<sub>1g</sub> = Σ<sub>g</sub><sup>+</sup>",
        "A<sub>2g</sub> = Σ<sub>g</sub><sup>\u2212</sup>",
        "E<sub>1g</sub> = Π<sub>g</sub>",
        "E<sub>2g</sub> = Δ<sub>g</sub>",
        "E<sub>3g</sub> = Φ<sub>g</sub>",
        "\u22ee",
        "A<sub>1u</sub> = Σ<sub>u</sub><sup>+</sup>",
        "A<sub>2u</sub> = Σ<sub>u</sub><sup>\u2212</sup>",
        "E<sub>1u</sub> = Π<sub>u</sub>",
        "E<sub>2u</sub> = Δ<sub>u</sub>",
        "E<sub>3u</sub> = Φ<sub>u</sub>",
        "\u22ee"
    });

    this->character_table_model->setHorizontalHeaderLabels({
        "E",
        "2 <i>C</i><sub>∞</sub>",
        "\u22ef",
        "∞ <i>σ</i><sub>v</sub>",
        "<i>i</i>",
        "2 <i>S</i><sub>∞</sub>",
        "\u22ef",
        "∞ <i>C</i><sub>2</sub>\u2032"
    });

    const std::vector<std::vector<QString>> characters = {
        {"1", "1", "\u22ef", "1", "1", "1", "\u22ef", "1"},
        {"1", "1", "\u22ef", "\u22121", "1", "1", "\u22ef", "\u22121"},
        {"2", "2 cos(φ)", "\u22ef", "0", "2", "\u22122 cos(φ)", "\u22ef", "0"},
        {"2", "2 cos(2φ)", "\u22ef", "0", "2", "2 cos(2φ)", "\u22ef", "0"},
        {"2", "2 cos(3φ)", "\u22ef", "0", "2", "\u22122 cos(3φ)", "\u22ef", "0"},
        {"\u22ee", "\u22ee", "\u22f1", "\u22ee", "\u22ee", "\u22ee", "\u22f1", "\u22ee"},
        {"1", "1", "\u22ef", "1", "\u22121", "\u22121", "\u22ef", "\u22121"},
        {"1", "1", "\u22ef", "\u22121", "\u22121", "\u22121", "\u22ef", "1"},
        {"2", "2 cos(φ)", "\u22ef", "0", "\u22122", "2 cos(φ)", "\u22ef", "0"},
        {"2", "2 cos(2φ)", "\u22ef", "0", "\u22122", "\u22122 cos(2φ)", "\u22ef", "0"},
        {"2", "2 cos(3φ)", "\u22ef", "0", "\u22122", "2 cos(3φ)", "\u22ef", "0"},
        {"\u22ee", "\u22ee", "\u22f1", "\u22ee", "\u22ee", "\u22ee", "\u22f1", "\u22ee"}
    };
    for (unsigned int i = 0; i < characters.size(); ++i) {
        for (unsigned int j = 0; j < characters[i].size(); ++j) {
            QStandardItem *item = new QStandardItem(characters[i][j]);
            item->setFlags(Qt::ItemFlag::NoItemFlags);
            item->setTextAlignment(Qt::AlignmentFlag::AlignCenter);
            this->character_table_model->setItem(i, j, item);
        }
    }
}

/**
 * @brief Update the selection in the point group model
 *
 * @param index index of point group in PointGroups::point_groups
 */
void CharacterTableDialog::update_point_group_selection(unsigned int index) {
    for (unsigned int i = 0; i < this->point_group_model->rowCount(); ++i) {
        QStandardItem* item = this->point_group_model->item(i);
        if (item->data(PointGroupItemDelegate::ItemDataRole::IndexRole).toUInt() == index) {
            this->point_group_view->selectionModel()->select(
                item->index(), QItemSelectionModel::SelectionFlag::ClearAndSelect);
            this->point_group_view->scrollTo(item->index());
        }
    }
}

/**
 * @brief Format a character coefficient
 *
 * @param number
 * @return QString
 */
QString CharacterTableDialog::format_number(double number) {
    // integer
    if (std::fmod(number, 1.0) == 0.0) {
        return QString::number(number).replace("-", "\u2212");
    }

    // float in the form 2 * cos(a * pi / b)
    unsigned int numerator, denominator;
    double abs_number = std::abs(number);
    if (abs_number == TC1P4) {
        numerator = 1; denominator = 4;
    } else if (abs_number == TC1P5) {
        numerator = 1; denominator = 5;
    } else if (abs_number == TC2P5) {
        numerator = 2; denominator = 5;
    } else if (abs_number == TC1P6) {
        numerator = 1; denominator = 6;
    } else if (abs_number == TC1P7) {
        numerator = 1; denominator = 7;
    } else if (abs_number == TC2P7) {
        numerator = 2; denominator = 7;
    } else if (abs_number == TC3P7) {
        numerator = 3; denominator = 7;
    } else if (abs_number == TC1P8) {
        numerator = 1; denominator = 8;
    } else if (abs_number == TC3P8) {
        numerator = 3; denominator = 8;
    } else if (abs_number == TC1P9) {
        numerator = 1; denominator = 9;
    } else if (abs_number == TC2P9) {
        numerator = 2; denominator = 9;
    } else if (abs_number == TC4P9) {
        numerator = 4; denominator = 9;
    } else if (abs_number == TC1P10) {
        numerator = 1; denominator = 10;
    } else if (abs_number == TC3P10) {
        numerator = 3; denominator = 10;
    } else {
        return QString::number(number, 'g', 4).replace("-", "\u2212");
    }

    QString sign = (number < 0) ? "\u2212" : "";
    QString numerator_str = (numerator > 1) ? QString::number(numerator) : "";

    return sign + QString("2 cos(%1π/%2)").arg(numerator_str).arg(denominator);
}

/**
 * @brief Select a point group from the point group model
 *
 * @param selected
 */
void CharacterTableDialog::select_point_group(const QItemSelection& selected) {
    QModelIndexList indices = selected.indexes();
    if (indices.size() < 1) return;

    unsigned int vector_index = indices[0].data(PointGroupItemDelegate::ItemDataRole::IndexRole).toUInt();
    this->show_point_group(vector_index);
}
