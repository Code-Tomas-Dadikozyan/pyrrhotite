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

#include <string>
#include <vector>
#include <boost/test/unit_test.hpp>
#include <glm/glm.hpp>
#include <glm/gtc/epsilon.hpp>
#include "../src/structure.h"
#include "utils.h"

BOOST_AUTO_TEST_SUITE(structure);

BOOST_AUTO_TEST_CASE(load_file) {
    std::string file = resolve_path("test/files/water.xyz");
    Structure struc(file);

    BOOST_TEST(struc.get_num_atoms() == 3);

    std::vector<unsigned int> atomic_numbers = struc.get_atomic_numbers();
    std::vector<unsigned int> expected_atomic_numbers{8, 1, 1};
    BOOST_CHECK_EQUAL_COLLECTIONS(atomic_numbers.begin(), atomic_numbers.end(),
                                  expected_atomic_numbers.begin(), expected_atomic_numbers.end());

    std::vector<glm::vec3> expected_coordinates{
        glm::vec3(0, 0, .0641751),
        glm::vec3(0, .753989, -.5092939),
        glm::vec3(0, -.753989, -.5092939)
    };

    for (unsigned int i = 0; i < struc.get_num_atoms(); ++i) {
        BOOST_TEST(glm::all(glm::epsilonEqual(struc.get_coordinates(i), expected_coordinates[i], 1e-6f)));
    }

    BOOST_TEST(struc.get_description() == "Water (HF/6-31G*) (C2v)");
    BOOST_TEST(struc.get_filename() == "water.xyz");
}

BOOST_AUTO_TEST_CASE(bonds) {
    std::string file = resolve_path("test/files/buckminsterfullerene.xyz");
    Structure struc(file);

    BOOST_TEST(struc.get_num_atoms() == 60);

    auto pairs = struc.calculate_bond_pairs();

    BOOST_TEST(pairs.size() == 90);
}

BOOST_AUTO_TEST_SUITE_END();
