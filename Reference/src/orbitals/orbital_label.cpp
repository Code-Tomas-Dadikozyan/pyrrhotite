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

#include "orbital_label.h"

/**
 * @brief Default constructor
 */
OrbitalLabel::OrbitalLabel() {}

/**
 * @brief Construct a new Orbital Label object
 *
 * @param principal principal quantum number
 * @param azimuthal azimuthal quantum number
 */
OrbitalLabel::OrbitalLabel(unsigned int principal, unsigned int azimuthal) {
    this->principal = principal;
    this->azimuthal = azimuthal;
    this->magnetic = 0;
    this->check_validity();
}

/**
 * @brief Construct a new Orbital Label object
 *
 * @param principal principal quantum number
 * @param azimuthal azimuthal quantum number
 * @param magnetic magnetic quantum number
 */
OrbitalLabel::OrbitalLabel(unsigned int principal, unsigned int azimuthal, int magnetic) {
    this->principal = principal;
    this->azimuthal = azimuthal;
    this->magnetic = magnetic;
    this->check_validity();
}

/**
 * @brief Get the principal quantum number
 *
 * @return const unsigned int
 */
const unsigned int OrbitalLabel::get_principal() const {
    return this->principal;
}

/**
 * @brief Get the azimuthal quantum number
 *
 * @return const unsigned int
 */
const unsigned int OrbitalLabel::get_azimuthal() const {
    return this->azimuthal;
}

/**
 * @brief Get the magnetic quantum number
 *
 * @return const int
 */
const int OrbitalLabel::get_magnetic() const {
    return this->magnetic;
}

/**
 * @brief Get the name of this orbital in plaintext
 *
 * @return const std::string
 */
const std::string OrbitalLabel::get_name() const {
    std::string name = std::to_string(this->principal);

    switch (this->azimuthal) {
        case 0:
            name += "s";
            break;
        case 1:
            name += "p";
            break;
    }

    if (this->azimuthal == 1) {
        switch (this->magnetic) {
            case -1:
                name += "y";
                break;
            case 0:
                name += "z";
                break;
            case 1:
                name += "x";
                break;
        }
    }

    return name;
}

/**
 * @brief Get the name of this orbital in HTML formatting
 *
 * @return const std::string
 */
const std::string OrbitalLabel::get_name_html() const {
    std::string name = std::to_string(this->principal);

    switch (this->azimuthal) {
        case 0:
            name += "s";
            break;
        case 1:
            name += "p";
            break;
    }

    if (this->azimuthal == 1) {
        switch (this->magnetic) {
            case -1:
                name += "<sub><i>y</i></sub>";
                break;
            case 0:
                name += "<sub><i>z</i></sub>";
                break;
            case 1:
                name += "<sub><i>x</i></sub>";
                break;
        }
    }

    return name;
}

/**
 * @brief Get the orbital label from a string representing the orbital
 *
 * @param orbital_string
 * @return OrbitalLabel
 */
OrbitalLabel OrbitalLabel::get_orbital_label(std::string orbital_string) {
    std::unordered_map<std::string, OrbitalLabel>::const_iterator it =
        OrbitalLabel::string_to_orbital.find(orbital_string);

    if (it == OrbitalLabel::string_to_orbital.end()) {
        throw std::runtime_error("Invalid orbital encountered: " + orbital_string);
    }

    return it->second;
}

/**
 * @brief Check whether this orbital is valid and throw an error if it is
 * not
 */
void OrbitalLabel::check_validity() {
    if (this->principal == 0) {
        throw std::runtime_error("Invalid principal quantum number");
    }
    if (this->azimuthal >= this->principal) {
        throw std::runtime_error("Invalid azimuthal quantum number");
    }
    int magnetic_abs = (this->magnetic < 0) ? -this->magnetic : this->magnetic;
    if (magnetic_abs > this->azimuthal) {
        throw std::runtime_error("Invalid magnetic quantum number");
    }

    // current implementation is limited to 1s, 2s, 2p
    if (this->principal > 2) {
        throw std::runtime_error("Unsupported principal quantum number");
    }
    if (this->azimuthal > 1) {
        throw std::runtime_error("Unsupported azimuthal quantum number");
    }
    if (magnetic_abs > 1) {
        throw std::runtime_error("Unsupported magnetic quantum number");
    }
}

/**
 * @brief Mapping from string to orbital label
 */
const std::unordered_map<std::string, OrbitalLabel> OrbitalLabel::string_to_orbital = {
    {"1s", OrbitalLabel(1, 0)},
    {"2s", OrbitalLabel(2, 0)},
    {"2px", OrbitalLabel(2, 1, 1)},
    {"2py", OrbitalLabel(2, 1, -1)},
    {"2pz", OrbitalLabel(2, 1, 0)}
};
