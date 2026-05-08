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

#include "operation_label_count.h"

/**
 * @brief Default constructor
 */
OperationLabelCount::OperationLabelCount() {}

/**
 * @brief Construct a new Operation Label Count object
 *
 * @param count number of similar operations with the label
 * @param label operation label
 */
OperationLabelCount::OperationLabelCount(unsigned int count, OperationLabel label) {
    this->count = count;
    this->label = label;
}

/**
 * @brief Construct a new Operation Label Count object
 *
 * @param label operation label
 */
OperationLabelCount::OperationLabelCount(OperationLabel label) {
    this->count = 1;
    this->label = label;
}

/**
 * @brief Get the number of similar operations with this label
 *
 * @return const unsigned int
 */
const unsigned int OperationLabelCount::get_count() const {
    return this->count;
}

/**
 * @brief Get the operation label
 *
 * @return OperationLabel&
 */
OperationLabel& OperationLabelCount::get_label() {
    return this->label;
}

/**
 * @brief Get the name of this symmetry operation in plaintext
 *
 * @return const std::string
 */
const std::string OperationLabelCount::get_name() const {
    return this->get_count_prefix() + this->label.get_name() + ((this->count > 1) ? "s" : "");
}

/**
 * @brief Get the name of this symmetry operation in HTML formatting
 *
 * @return const std::string
 */
const std::string OperationLabelCount::get_name_html() const {
    return this->get_count_prefix() + this->label.get_name_html() + ((this->count > 1) ? "s" : "");
}

/**
 * @brief Get the short name of this symmetry operation in plaintext
 *
 * @return const std::string
 */
const std::string OperationLabelCount::get_short_name() const {
    return this->get_count_prefix() + this->label.get_short_name();
}

/**
 * @brief Get the short name of this symmetry operation in HTML formatting
 *
 * @return const std::string
 */
const std::string OperationLabelCount::get_short_name_html() const {
    return this->get_count_prefix() + this->label.get_short_name_html();
}

/**
 * @brief Get the count prefix of this operation label
 *
 * @return const std::string
 */
const std::string OperationLabelCount::get_count_prefix() const {
    if (this->count > 1) {
        return std::to_string(this->count) + " ";
    } else if (this->count == 0) {
        return std::string("∞ ");
    } else {
        return "";
    }
}
