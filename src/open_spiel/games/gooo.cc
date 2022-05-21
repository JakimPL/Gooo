// Copyright 2019 DeepMind Technologies Limited
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "open_spiel/games/gooo.h"

#include <algorithm>
#include <memory>
#include <utility>
#include <vector>

#include "open_spiel/spiel_utils.h"
#include "open_spiel/utils/tensor_view.h"

namespace open_spiel
{
namespace gooo
{
namespace
{

// Facts about the game.
const GameType kGameType{
    /*short_name=*/"gooo",
    /*long_name=*/"Gooo",
    GameType::Dynamics::kSequential,
    GameType::ChanceMode::kDeterministic,
    GameType::Information::kPerfectInformation,
    GameType::Utility::kConstantSum,
    GameType::RewardModel::kTerminal,
    /*max_num_players=*/2,
    /*min_num_players=*/2,
    /*provides_information_state_string=*/true,
    /*provides_information_state_tensor=*/false,
    /*provides_observation_string=*/true,
    /*provides_observation_tensor=*/true,
    /*parameter_specification=*/{
        {"board_size", GameParameter(6)}
    } // no parameters
};

std::shared_ptr<const Game> Factory(const GameParameters &params)
{
    return std::shared_ptr<const Game>(new GoooGame(params));
}

REGISTER_SPIEL_GAME(kGameType, Factory);

} // namespace

std::string GoooState::StateToString(Player player) const
{
    switch (player) {
    case 0:
        return "x";
    case 1:
        return "o";
    default:
        SpielFatalError("Unknown player.");
    }
}

void GoooState::DoApplyAction(Action move)
{
    state_[current_player_][move] += 1;
    num_moves_ += 1;

    if (IsTerminal()) {
        if (points_ > 0) {
            outcome_ = 0;
        } else if (points_ < 0) {
            outcome_ = 1;
        }
    } else if (LegalActionsForPlayer(1 - current_player_).empty()) {
        points_ += current_player_ ? -1 : 1;
    } else {
        current_player_ = 1 - current_player_;
    }
}

bool GoooState::IsMovePossible(Player player, Action action_id) const
{
    const int position = state_[player][action_id];
    if (position > kNumSize) {
        return false;
    }

    return position == kNumSize or (position < kNumSize and state_[1 - player][position] != action_id + 1);
}

std::vector<Action> GoooState::LegalActions() const
{
    return LegalActionsForPlayer(current_player_);
}

std::vector<Action> GoooState::LegalActionsForPlayer(Player player) const
{
    if (IsTerminal())
        return {};

    std::vector<Action> moves;
    for (Action action_id = 0; action_id < kNumSize; ++action_id) {
        if (IsMovePossible(player, action_id)) {
            moves.push_back(action_id);
        }
    }

    return moves;
}

std::string GoooState::ActionToString(Player player, Action action_id) const
{
    return absl::StrCat("(", StateToString(player), ": ", action_id + 1, ")");
}

GoooState::GoooState(std::shared_ptr<const Game> game, int board_size) : State(game),
    kNumSize(board_size),
    kNumBoardLength(board_size + 1),
    kNumCells((board_size + 1) * (board_size + 1))
{
    std::vector<int> init;
    init.resize(board_size);
    state_ = {init, init};
    points_ = 0;
}

std::string GoooState::ToString() const
{
    std::string str = current_player_ ? "Red" : "Blue";
    str += " player turn\n";
    for (int c = 0; c <= kNumSize; ++c) {
        for (int r = 0; r <= kNumSize; ++r) {
            if (r > 0 and state_[1][r - 1] == c) {
                absl::StrAppend(&str, "x");
            } else if (c > 0 and state_[0][c - 1] == r) {
                absl::StrAppend(&str, "o");
            } else if (c > 0 and r > 0) {
                absl::StrAppend(&str, ".");
            } else {
                absl::StrAppend(&str, " ");
            }
        }

        absl::StrAppend(&str, "\n");
    }

    absl::StrAppend(&str, "Points: ", points_);

    return str;
}

bool GoooState::IsTerminal() const
{
    for (int player = 0; player < 2; ++player) {
        bool terminal = true;
        for (int position = 0; position < kNumSize; ++position) {
            if (state_[player][position] <= kNumSize) {
                terminal = false;
                break;
            }
        }

        if (terminal) {
            return true;
        }
    }

    return false;
}

std::vector<double> GoooState::Returns() const
{
    if (points_ > 0) {
        return {1.0, -1.0};
    } else if (points_ < 0) {
        return {-1.0, 1.0};
    } else {
        return {0.0, 0.0};
    }
}

std::string GoooState::InformationStateString(Player player) const
{
    SPIEL_CHECK_GE(player, 0);
    SPIEL_CHECK_LT(player, num_players_);
    return HistoryString();
}

std::string GoooState::ObservationString(Player player) const
{
    SPIEL_CHECK_GE(player, 0);
    SPIEL_CHECK_LT(player, num_players_);
    return ToString();
}

void GoooState::ObservationTensor(Player player, absl::Span<float> values) const
{
    SPIEL_CHECK_GE(player, 0);
    SPIEL_CHECK_LT(player, num_players_);

    TensorView<2> view(values, {kNumStates, kNumCells}, true);
    for (int player = 0; player < 2; ++player) {
        for (int position = 0; position < kNumSize; ++position) {
            const int value = state_[player][position];
            if (value < kNumSize) {
                const int cell = player ? value * (kNumSize + 1) + (position + 1) : (position + 1) * (kNumSize + 1) + value;
                view[ {player, cell} ] = 1.0;
            }
        }
    }
}

void GoooState::UndoAction(Player player, Action move)
{
    state_[player][move] -= 1;
    current_player_ = player;
    outcome_ = kInvalidPlayer;
    num_moves_ -= 1;
    history_.pop_back();
    --move_number_;
}

std::unique_ptr<State> GoooState::Clone() const
{
    return std::unique_ptr<State>(new GoooState(*this));
}

GoooGame::GoooGame(const GameParameters &params)
    : Game(kGameType, params),
      kNumSize(ParameterValue<int>("board_size")),
      kNumBoardLength(ParameterValue<int>("board_size") + 1),
      kNumCells((ParameterValue<int>("board_size") + 1) * (ParameterValue<int>("board_size") + 1)) {}

} // namespace gooo
} // namespace open_spiel
