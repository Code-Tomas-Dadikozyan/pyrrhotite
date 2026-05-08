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

#ifndef SYMMETRY_OPERATIONS_OPERATION_LABEL_H
#define SYMMETRY_OPERATIONS_OPERATION_LABEL_H

#include <algorithm>
#include <stdexcept>
#include <string>
#include <glm/glm.hpp>

class OperationLabel {
public:
    enum class Element : unsigned char {
        ProperRotation,
        Inversion,
        ImproperRotation,
        Reflection,

        C = ProperRotation,
        I = Inversion,
        S = ImproperRotation,
        sigma = Reflection
    };

    enum class Plane : unsigned char {
        None,
        Horizontal,
        Vertical,
        Dihedral,

        h = Horizontal,
        v = Vertical,
        d = Dihedral
    };

    enum class Prime : unsigned char {
        None,
        Single,
        Double
    };

    static const unsigned int DEGREE_INF = 0;

private:
    Element element;
    unsigned int degree;
    int multiple;
    Plane plane;
    Prime prime;

public:
    /**
     * @brief Default constructor
     */
    OperationLabel();

    /**
     * @brief Construct a new Operation Label object
     *
     * @param element symmetry element
     * @param degree degree of symmetry element
     * @param multiple multiple of degree
     * @param plane plane in which the operation occurs
     * @param prime distinguish similar operations
     */
    OperationLabel(Element element, unsigned int degree, int multiple, Plane plane, Prime prime);

    /**
     * @brief Construct a new Operation Label object
     *
     * @param element symmetry element
     */
    OperationLabel(Element element);

    /**
     * @brief Construct a new Operation Label object
     *
     * @param element symmetry element
     * @param degree degree of symmetry element
     */
    OperationLabel(Element element, unsigned int degree);

    /**
     * @brief Construct a new Operation Label object
     *
     * @param element symmetry element
     * @param degree degree of symmetry element
     * @param multiple multiple of degree
     */
    OperationLabel(Element element, unsigned int degree, int multiple);

    /**
     * @brief Construct a new Operation Label object
     *
     * @param element symmetry element
     * @param degree degree of symmetry element
     * @param prime distinguish similar operations
     */
    OperationLabel(Element element, unsigned int degree, Prime prime);

    /**
     * @brief Construct a new Operation Label object
     *
     * @param element symmetry element
     * @param plane plane in which the operation occurs
     */
    OperationLabel(Element element, Plane plane);

    /**
     * @brief Construct a new Operation Label object
     *
     * @param element symmetry element
     * @param plane plane in which the operation occurs
     * @param prime distinguish similar operations
     */
    OperationLabel(Element element, Plane plane, Prime prime);

    /**
     * @brief Get the element of this symmetry operation
     *
     * @return const Element
     */
    const Element get_element() const;

    /**
     * @brief Get the degree of this symmetry operation
     *
     * @return const unsigned int
     */
    const unsigned int get_degree() const;

    /**
     * @brief Get the multiple of this symmetry operation
     *
     * @return const int
     */
    const int get_multiple() const;

    /**
     * @brief Set the multiple of this symmetry operation
     *
     * @param multiple
     */
    void set_multiple(int multiple);

    /**
     * @brief Get the plane of this symmetry operation
     *
     * @return const Plane
     */
    const Plane get_plane() const;

    /**
     * @brief Set the plane of this symmetry operation
     *
     * @param plane
     */
    void set_plane(Plane plane);

    /**
     * @brief Get the prime of this symmetry operation
     *
     * @return const Prime
     */
    const Prime get_prime() const;

    /**
     * @brief Set the prime of this symmetry operation
     *
     * @param prime
     */
    void set_prime(Prime prime);

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

    /**
     * @brief Get the colour of this symmetry operation (rgb)
     *
     * @return const glm::vec3
     */
    const glm::vec3 get_colour() const;

    /**
     * @brief Check whether this symmetry operation matches another symmetry
     * operation
     *
     * This check does not take multiplicity into account.
     *
     * @param other other symmetry operation
     * @return true if operations match
     * @return false if operations don't match
     */
    const bool matches(OperationLabel& other) const;

    /**
     * @brief Check whether this symmetry operation matches another symmetry
     * operation
     *
     * This check takes the absolute value of the multiplicity into account.
     *
     * @param other other symmetry operation
     * @return true if operations match
     * @return false if operations don't match
     */
    const bool matches_strict(OperationLabel& other) const;

private:
    /**
     * @brief Format a number for string output
     *
     * @param number number to format
     * @return const std::string formatted number
     */
    const std::string format_number(int number) const;

    /**
     * @brief Get the suffix of the name of this symmetry operation
     *
     * @return const std::string
     */
    const std::string get_name_suffix() const;
};

#endif  // SYMMETRY_OPERATIONS_OPERATION_LABEL_H
