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

#ifndef SYMMETRY_OPERATIONS_OPERATION_LABEL_COUNT_H
#define SYMMETRY_OPERATIONS_OPERATION_LABEL_COUNT_H

#include <string>
#include "operation_label.h"

class OperationLabelCount {
private:
    unsigned int count;
    OperationLabel label;

public:
    static const unsigned int COUNT_INF = 0;

public:
    /**
     * @brief Default constructor
     */
    OperationLabelCount();

    /**
     * @brief Construct a new Operation Label Count object
     *
     * @param count number of similar operations with this label
     * @param label operation label
     */
    OperationLabelCount(unsigned int count, OperationLabel label);

    /**
     * @brief Construct a new Operation Label Count object
     *
     * @param label operation label
     */
    OperationLabelCount(OperationLabel label);

    /**
     * @brief Get the number of similar operations with this label
     *
     * @return const unsigned int
     */
    const unsigned int get_count() const;

    /**
     * @brief Get the operation label
     *
     * @return OperationLabel&
     */
    OperationLabel& get_label();

    /**
     * @brief Get the name of this symmetry operation in plaintext
     *
     * @return const std::string
     */
    const std::string get_name() const;

    /**
     * @brief Get the name of this symmetry operation in HTML formatting
     *
     * @return const std::string
     */
    const std::string get_name_html() const;

    /**
     * @brief Get the short name of this symmetry operation in plaintext
     *
     * @return const std::string
     */
    const std::string get_short_name() const;

    /**
     * @brief Get the short name of this symmetry operation in HTML formatting
     *
     * @return const std::string
     */
    const std::string get_short_name_html() const;

private:
    /**
     * @brief Get the count prefix of this operation label
     *
     * @return const std::string
     */
    const std::string get_count_prefix() const;
};

#endif  // SYMMETRY_OPERATIONS_OPERATION_LABEL_COUNT_H
