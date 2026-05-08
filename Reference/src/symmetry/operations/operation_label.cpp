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

#include "operation_label.h"

/**
 * @brief Default constructor
 */
OperationLabel::OperationLabel() {}

/**
 * @brief Construct a new Operation Label object
 *
 * @param element symmetry element
 * @param degree degree of symmetry element
 * @param multiple multiple of degree
 * @param plane plane in which the operation occurs
 * @param prime distinguish similar operations
 */
OperationLabel::OperationLabel(Element element, unsigned int degree, int multiple, Plane plane, Prime prime) {
    this->element = element;
    this->degree = degree;
    this->multiple = multiple;
    this->plane = plane;
    this->prime = prime;
}

/**
 * @brief Construct a new Operation Label object
 *
 * @param element symmetry element
 */
OperationLabel::OperationLabel(Element element) {
    this->element = element;
    this->degree = 0;
    this->multiple = 1;
    this->plane = Plane::None;
    this->prime = Prime::None;
}

/**
 * @brief Construct a new Operation Label object
 *
 * @param element symmetry element
 * @param degree degree of symmetry element
 */
OperationLabel::OperationLabel(Element element, unsigned int degree) {
    this->element = element;
    this->degree = degree;
    this->multiple = 1;
    this->plane = Plane::None;
    this->prime = Prime::None;
}

/**
 * @brief Construct a new Operation Label object
 *
 * @param element symmetry element
 * @param degree degree of symmetry element
 * @param multiple multiple of degree
 */
OperationLabel::OperationLabel(Element element, unsigned int degree, int multiple) {
    this->element = element;
    this->degree = degree;
    this->multiple = multiple;
    this->plane = Plane::None;
    this->prime = Prime::None;
}

/**
 * @brief Construct a new Operation Label object
 *
 * @param element symmetry element
 * @param degree degree of symmetry element
 * @param prime distinguish similar operations
 */
OperationLabel::OperationLabel(Element element, unsigned int degree, Prime prime) {
    this->element = element;
    this->degree = degree;
    this->multiple = 1;
    this->plane = Plane::None;
    this->prime = prime;
}

/**
 * @brief Construct a new Operation Label object
 *
 * @param element symmetry element
 * @param plane plane in which the operation occurs
 */
OperationLabel::OperationLabel(Element element, Plane plane) {
    this->element = element;
    this->degree = 0;
    this->multiple = 1;
    this->plane = plane;
    this->prime = Prime::None;
}

/**
 * @brief Construct a new Operation Label object
 *
 * @param element symmetry element
 * @param plane plane in which the operation occurs
 * @param prime distinguish similar operations
 */
OperationLabel::OperationLabel(Element element, Plane plane, Prime prime) {
    this->element = element;
    this->degree = 0;
    this->multiple = 1;
    this->plane = plane;
    this->prime = prime;
}

/**
 * @brief Get the element of this symmetry operation
 *
 * @return const Element
 */
const OperationLabel::Element OperationLabel::get_element() const {
    return this->element;
}

/**
 * @brief Get the degree of this symmetry operation
 *
 * @return const unsigned int
 */
const unsigned int OperationLabel::get_degree() const {
    return this->degree;
}

/**
 * @brief Get the multiple of this symmetry operation
 *
 * @return const int
 */
const int OperationLabel::get_multiple() const {
    return this->multiple;
}

/**
 * @brief Set the multiple of this symmetry operation
 *
 * @param multiple
 */
void OperationLabel::set_multiple(int multiple) {
    this->multiple = multiple;
}

/**
 * @brief Get the plane of this symmetry operation
 *
 * @return const Plane
 */
const OperationLabel::Plane OperationLabel::get_plane() const {
    return this->plane;
}

/**
 * @brief Set the plane of this symmetry operation
 *
 * @param plane
 */
void OperationLabel::set_plane(Plane plane) {
    this->plane = plane;
}

/**
 * @brief Get the prime of this symmetry operation
 *
 * @return const Prime
 */
const OperationLabel::Prime OperationLabel::get_prime() const {
    return this->prime;
}

/**
 * @brief Set the prime of this symmetry operation
 *
 * @param prime
 */
void OperationLabel::set_prime(Prime prime) {
    this->prime = prime;
}

/**
 * @brief Get the name of this symmetry operation in plaintext
 *
 * @return const std::string
 */
const std::string OperationLabel::get_name() const {
    return this->get_short_name() + this->get_name_suffix();
}

/**
 * @brief Get the name of this symmetry operation in HTML formatting
 *
 * @return const std::string
 */
const std::string OperationLabel::get_name_html() const {
    return this->get_short_name_html() + this->get_name_suffix();
}

/**
 * @brief Get the short name of this symmetry operation in plaintext
 *
 * @return const std::string
 */
const std::string OperationLabel::get_short_name() const {
    std::string degree = this->format_number(this->degree);
    std::string multiple = this->format_number(this->multiple);

    std::string symbol;

    switch (this->element) {
        case Element::ProperRotation:
            symbol = "C";
            break;
        case Element::Inversion:
            symbol = "i";
            break;
        case Element::ImproperRotation:
            symbol = "S";
            break;
        case Element::Reflection:
            symbol = "σ";
            break;
        default:
            throw std::runtime_error("Unexpected symmetry element encountered.");
    }

    std::string name = symbol;

    // degree and multiple
    if (this->element == Element::ProperRotation || this->element == Element::ImproperRotation) {
        name += (this->degree != DEGREE_INF) ? degree : "∞";
        name += (this->multiple != 1) ? "^" + multiple : "";
    }

    // plane
    if (this->element == Element::Reflection && this->plane != Plane::None) {
        switch (this->plane) {
            case Plane::Horizontal:
                name += "h";
                break;
            case Plane::Vertical:
                name += "v";
                break;
            case Plane::Dihedral:
                name += "d";
                break;
            default:
                throw std::runtime_error("Unexpected symmetry plane encountered.");
        }
    }

    // prime
    if (this->prime != Prime::None) {
        switch (this->prime) {
            case Prime::Single:
                name += "\u2032";
                break;
            case Prime::Double:
                name += "\u2033";
                break;
            default:
                throw std::runtime_error("Unexpected symmetry prime encountered.");
        }
    }

    return name;
}

/**
 * @brief Get the short name of this symmetry operation in HTML formatting
 *
 * @return const std::string
 */
const std::string OperationLabel::get_short_name_html() const {
    std::string degree = this->format_number(this->degree);
    std::string multiple = this->format_number(this->multiple);

    std::string symbol;

    switch (this->element) {
        case Element::ProperRotation:
            symbol = "<i>C</i>";
            break;
        case Element::Inversion:
            symbol = "<i>i</i>";
            break;
        case Element::ImproperRotation:
            symbol = "<i>S</i>";
            break;
        case Element::Reflection:
            symbol = "<i>σ</i>";
            break;
        default:
            throw std::runtime_error("Unexpected symmetry element encountered.");
    }

    std::string name = symbol;

    // degree and multiple
    if (this->element == Element::ProperRotation || this->element == Element::ImproperRotation) {
        name += (this->degree != 0) ? "<sub>" + degree + "</sub>" : "<sub>∞</sub>";
        name += (this->multiple != 1) ? "<sup>" + multiple + "</sup>" : "";
    }

    // plane
    if (this->element == Element::Reflection && this->plane != Plane::None) {
        switch (this->plane) {
            case Plane::Horizontal:
                name += "<sub>h</sub>";
                break;
            case Plane::Vertical:
                name += "<sub>v</sub>";
                break;
            case Plane::Dihedral:
                name += "<sub>d</sub>";
                break;
            default:
                throw std::runtime_error("Unexpected symmetry plane encountered.");
        }
    }

    // prime
    if (this->prime != Prime::None) {
        switch (this->prime) {
            case Prime::Single:
                name += "\u2032";
                break;
            case Prime::Double:
                name += "\u2033";
                break;
            default:
                throw std::runtime_error("Unexpected symmetry prime encountered.");
        }
    }

    return name;
}

/**
 * @brief Get the colour of this symmetry operation (rgb)
 *
 * @return const glm::vec3
 */
const glm::vec3 OperationLabel::get_colour() const {
    float l = std::min(1.0, 0.7 / this->degree + 0.4);
    switch (this->element) {
        case Element::ProperRotation:
            return glm::vec3(0.0, l, 0.0);
        case Element::Inversion:
            return glm::vec3(0.6, 0.0, 0.0);
        case Element::ImproperRotation:
            return glm::vec3(0.0, l, l);
        case Element::Reflection:
            return glm::vec3(0.0, 0.0, 0.6);
        default:
            throw std::runtime_error("Unexpected symmetry element encountered.");
    }
}

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
const bool OperationLabel::matches(OperationLabel& other) const {
    return
        this->element == other.element &&
        this->degree == other.degree &&
        this->plane == other.plane &&
        this->prime == other.prime;
}

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
const bool OperationLabel::matches_strict(OperationLabel& other) const {
    return this->matches(other) &&
        (this->multiple == other.multiple || this->multiple == -other.multiple);
}

/**
 * @brief Format a number for string output
 *
 * @param number number to format
 * @return const std::string formatted number
 */
const std::string OperationLabel::format_number(int number) const {
    if (number < 0) {
        return "\u2212" + std::to_string(std::abs(number));
    } else {
        return std::to_string(number);
    }
}

/**
 * @brief Get the suffix of the name of this symmetry operation
 *
 * @return const std::string
 */
const std::string OperationLabel::get_name_suffix() const {
    std::string suffix;

    switch (this->element) {
        case Element::ProperRotation:
            suffix = " rotation";
            break;
        case Element::Inversion:
            suffix = " inversion";
            break;
        case Element::ImproperRotation:
            suffix = " improper rotation";
            break;
        case Element::Reflection:
            suffix = " reflection";
            break;
        default:
            throw std::runtime_error("Unexpected symmetry element encountered.");
    }

    return suffix;
}
