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

#ifndef ORBITALS_ORBITAL_LABEL_H
#define ORBITALS_ORBITAL_LABEL_H

#include <stdexcept>
#include <string>
#include <unordered_map>

class OrbitalLabel {
private:
    unsigned int principal;
    unsigned int azimuthal;
    int magnetic;

public:
    /**
     * @brief Default constructor
     */
    OrbitalLabel();

    /**
     * @brief Construct a new Orbital Label object
     *
     * @param principal principal quantum number
     * @param azimuthal azimuthal quantum number
     */
    OrbitalLabel(unsigned int principal, unsigned int azimuthal);

    /**
     * @brief Construct a new Orbital Label object
     *
     * @param principal principal quantum number
     * @param azimuthal azimuthal quantum number
     * @param magnetic magnetic quantum number
     */
    OrbitalLabel(unsigned int principal, unsigned int azimuthal, int magnetic);

    /**
     * @brief Get the principal quantum number
     *
     * @return const unsigned int
     */
    const unsigned int get_principal() const;

    /**
     * @brief Get the azimuthal quantum number
     *
     * @return const unsigned int
     */
    const unsigned int get_azimuthal() const;

    /**
     * @brief Get the magnetic quantum number
     *
     * @return const int
     */
    const int get_magnetic() const;

    /**
     * @brief Get the name of this orbital in plaintext
     *
     * @return const std::string
     */
    const std::string get_name() const;

    /**
     * @brief Get the name of this orbital in HTML formatting
     *
     * @return const std::string
     */
    const std::string get_name_html() const;

    /**
     * @brief Get the orbital label from a string representing the orbital
     *
     * @param orbital_string
     * @return OrbitalLabel
     */
    static OrbitalLabel get_orbital_label(std::string orbital_string);

private:
    /**
     * @brief Mapping from string to orbital label
     */
    static const std::unordered_map<std::string, OrbitalLabel> string_to_orbital;

    /**
     * @brief Check whether this orbital is valid and throw an error if it is
     * not
     */
    void check_validity();
};

#endif  // ORBITAL_LABEL_H
