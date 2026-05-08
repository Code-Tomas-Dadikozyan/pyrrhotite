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

#ifndef SYMMETRY_POINT_GROUPS_POINT_GROUPS_H
#define SYMMETRY_POINT_GROUPS_POINT_GROUPS_H

#include <cmath>
#include <math.h>
#include <vector>
#include "../irreps/irrep_label.h"
#include "../operations/operation.h"
#include "../operations/operation_label.h"
#include "point_group.h"
#include "point_group_label.h"

typedef PointGroupLabel Label;
typedef PointGroupLabel::Class Class;
typedef OperationLabel O;
typedef OperationLabel::Element E;
typedef OperationLabel::Plane OPlane;
typedef OperationLabel::Prime OPrime;
typedef IrrepLabel I;
typedef IrrepLabel::Mulliken M;
typedef IrrepLabel::Parity IParity;
typedef IrrepLabel::Prime IPrime;

#define TC1P4  (2.0 * std::cos(1.0 * M_PI / 4.0))   // 1.4142
#define TC1P5  (2.0 * std::cos(1.0 * M_PI / 5.0))   // 1.6180
#define TC2P5  (2.0 * std::cos(2.0 * M_PI / 5.0))   // 0.6180
#define TC1P6  (2.0 * std::cos(1.0 * M_PI / 6.0))   // 1.7321
#define TC1P7  (2.0 * std::cos(1.0 * M_PI / 7.0))   // 1.8019
#define TC2P7  (2.0 * std::cos(2.0 * M_PI / 7.0))   // 1.2470
#define TC3P7  (2.0 * std::cos(3.0 * M_PI / 7.0))   // 0.4450
#define TC1P8  (2.0 * std::cos(1.0 * M_PI / 8.0))   // 1.8478
#define TC3P8  (2.0 * std::cos(3.0 * M_PI / 8.0))   // 0.7654
#define TC1P9  (2.0 * std::cos(1.0 * M_PI / 9.0))   // 1.8794
#define TC2P9  (2.0 * std::cos(2.0 * M_PI / 9.0))   // 1.5321
#define TC4P9  (2.0 * std::cos(4.0 * M_PI / 9.0))   // 0.3473
#define TC1P10 (2.0 * std::cos(1.0 * M_PI / 10.0))  // 1.9021
#define TC3P10 (2.0 * std::cos(3.0 * M_PI / 10.0))  // 1.1756

class PointGroups final {
public:
    /**
     * @brief List of supported point groups
     */
    static const std::vector<PointGroup> point_groups;
};

#endif  // SYMMETRY_POINT_GROUPS_POINT_GROUPS_H
