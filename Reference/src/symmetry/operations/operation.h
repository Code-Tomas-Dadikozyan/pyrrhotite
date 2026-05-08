/**
 * Schoenflies
 * Copyright (c) 2021 Luuk Kempen
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

#ifndef SYMMETRY_OPERATIONS_OPERATION_H
#define SYMMETRY_OPERATIONS_OPERATION_H

#include <algorithm>
#include <cmath>
#include <math.h>
#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <glm/glm.hpp>
#include "../../structure.h"
#include "operation_label.h"

class Structure;  // forward declaration

class Operation {
public:
    static const unsigned int DEGREE_INF = 0;

private:
    unsigned int id;

    OperationLabel label;

    unsigned int degree;
    glm::vec3 axis;

    glm::mat3x3 matrix;
    float error = NAN;
public:
    std::vector<unsigned int> result_indices_forwards;
    std::vector<unsigned int> result_indices_backwards;

public:
    /**
     * @brief Default constructor
     */
    Operation();

    /**
     * @brief Construct a new Operation object (inversion)
     *
     * @param element symmetry element to which this operation belongs
     */
    Operation(OperationLabel::Element element);

    /**
     * @brief Construct a new Operation object (reflection)
     *
     * @param element symmetry element to which this operation belongs
     * @param normal plane normal of this operation
     */
    Operation(OperationLabel::Element element, glm::vec3 normal);

    /**
     * @brief Construct a new Operation object (proper/improper rotation)
     *
     * @param element symmetry element to which this operation belongs
     * @param degree degree of the rotation
     * @param axis rotation axis of this operation
     */
    Operation(OperationLabel::Element element, unsigned int degree, glm::vec3 axis);

    /**
     * @brief Get the id of this symmetry operation
     *
     * @return unsigned int
     */
    const unsigned int get_id() const;

    /**
     * @brief Set the id of this symmetry operation
     *
     * @param id
     */
    void set_id(unsigned int id);

    /**
     * @brief Get the label of this symmetry operation
     *
     * @return OperationLabel&
     */
    OperationLabel& get_label();

    /**
     * @brief Set the label of this symmetry operation
     *
     * @param label
     */
    void set_label(OperationLabel label);

    /**
     * @brief Get the error of this symmetry operation
     *
     * @return const float
     */
    const float get_error() const;

    /**
     * @brief Get the degree of the operation as an integer
     *
     * @return const unsigned int
     */
    const unsigned int get_degree() const;

    /**
     * @brief Get the axis of the operation
     *
     * @return const glm::vec3
     */
    const glm::vec3 get_axis() const;

    /**
     * @brief Get the index of the atom overlapping the atom indicated with
     * index after applying this operation
     *
     * @param index
     * @return const unsigned int
     */
    const unsigned int get_result_index(unsigned int index) const;

    /**
     * @brief Check whether this operation equals another operation
     *
     * @param other other operation
     * @return true if equal
     * @return false if inequal
     */
    const bool operator==(Operation& other) const;

    /**
     * @brief Perform the symmetry operation and set the error value
     *
     * @param structure structure on which to perform the operation
     */
    void do_operation(std::shared_ptr<Structure> structure);

    /**
     * @brief Perform the symmetry operation on a single atom
     *
     * @param coordinates coordinates of the atom
     * @return const glm::vec3 coordinates after performing the operation
     */
    const glm::vec3 do_atom_operation(glm::vec3 coordinates) const;

    /**
     * @brief Get the distance from the provided coordinates to the symmetry
     * element to which this operation belongs
     *
     * @param coordinates coordinates from which to determine distance
     * @return const float distance
     */
    const float get_distance_to_element(glm::vec3 coordinates) const;

    /**
     * @brief Calculate a fractional operation matrix for this symmetry
     * operation
     *
     * If the fraction is not 1, the operation is applied partially, used in
     * animating the symmetry operation.
     *
     * @param f progress fraction of operation
     * @return const glm::mat3x3
     */
    const glm::mat3x3 calculate_fractional_matrix(double f) const;

private:
    /**
     * @brief Calculate the operation matrix for this symmetry operation
     *
     * @return glm::mat3x3
     */
    const glm::mat3x3 calculate_matrix() const;

    /**
     * @brief Calculate the operation matrix for an inversion
     *
     * @param f progress fraction of operation
     * @return glm::mat3x3
     */
    const glm::mat3x3 calculate_matrix_inversion(double f) const;

    /**
     * @brief Calculate the operation matrix for a proper rotation
     *
     * @param f progress fraction of operation
     * @return glm::mat3x3
     */
    const glm::mat3x3 calculate_matrix_proper_rotation(double f) const;

    /**
     * @brief Calculate the operation matrix for a reflection
     *
     * @param f progress fraction of operation
     * @return glm::mat3x3
     */
    const glm::mat3x3 calculate_matrix_reflection(double f) const;

    /**
     * @brief Calculate the operation matrix for an improper rotation
     *
     * @param f progress fraction of operation
     * @return glm::mat3x3
     */
    const glm::mat3x3 calculate_matrix_improper_rotation(double f) const;

    /**
     * @brief Get the distance from the provided coordinates to an inversion
     * centre
     *
     * @param coordinates coordinates from which to determine distance
     * @return const float distance
     */
    const float get_distance_to_inversion(glm::vec3 coordinates) const;

    /**
     * @brief Get the distance from the provided coordinates to a rotation axis
     *
     * @param coordinates coordinates from which to determine distance
     * @return const float distance
     */
    const float get_distance_to_rotation(glm::vec3 coordinates) const;

    /**
     * @brief Get the distance from the provided coordinates to a reflection
     * plane
     *
     * @param coordinates coordinates from which to determine distance
     * @return const float distance
     */
    const float get_distance_to_reflection(glm::vec3 coordinates) const;
};

#endif  // SYMMETRY_OPERATIONS_OPERATION_H
