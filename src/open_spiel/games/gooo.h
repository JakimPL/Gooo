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

#ifndef OPEN_SPIEL_GAMES_GOOO_H_
#define OPEN_SPIEL_GAMES_GOOO_H_

#include <array>
#include <map>
#include <memory>
#include <string>
#include <vector>

#include "open_spiel/spiel.h"

namespace open_spiel
{
namespace gooo
{

// Constants.
inline constexpr int kNumPlayers = 2;
inline constexpr int kNumStates = 1 + kNumPlayers;

// State of an in-play game.
class GoooState : public State
{
public:
    GoooState(std::shared_ptr<const Game> game, int board_size);

    GoooState(const GoooState &) = default;
    GoooState &operator=(const GoooState &) = default;

    Player CurrentPlayer() const override
    {
        return IsTerminal() ? kTerminalPlayerId : current_player_;
    }
    std::string ActionToString(Player player, Action action_id) const override;
    std::string ToString() const override;
    bool IsTerminal() const override;
    std::vector<double> Returns() const override;
    std::string InformationStateString(Player player) const override;
    std::string ObservationString(Player player) const override;
    void ObservationTensor(Player player, absl::Span<float> values) const override;
    std::unique_ptr<State> Clone() const override;
    void UndoAction(Player player, Action move) override;
    std::vector<Action> LegalActions() const override;
    Player outcome() const
    {
        return outcome_;
    }

protected:
    int points_ = 0;
    std::array<std::vector<int>, 2> state_;
    void DoApplyAction(Action move) override;
    bool IsMovePossible(Player player, Action move) const;
    std::string StateToString(Player player) const;
    std::vector<Action> LegalActionsForPlayer(Player player) const;

private:
    Player current_player_ = 0;
    Player outcome_ = kInvalidPlayer;
    int num_moves_ = 0;

    const int kNumSize;
    const int kNumBoardLength;
    const int kNumCells;
};

// Game object.
class GoooGame : public Game
{
public:
    explicit GoooGame(const GameParameters &params);
    int NumDistinctActions() const override
    {
        return kNumSize;
    }
    std::unique_ptr<State> NewInitialState() const override
    {
        return std::unique_ptr<State>(new GoooState(shared_from_this(), kNumSize));
    }
    int NumPlayers() const override
    {
        return kNumPlayers;
    }
    double MinUtility() const override
    {
        return -1;
    }
    double UtilitySum() const override
    {
        return 0;
    }
    double MaxUtility() const override
    {
        return 1;
    }
    std::vector<int> ObservationTensorShape() const override
    {
        return {kNumStates, kNumBoardLength, kNumBoardLength};
    }
    int MaxGameLength() const override
    {
        return 2 * kNumSize * kNumBoardLength;
    }

private:
    const int kNumSize;
    const int kNumBoardLength;
    const int kNumCells;
};

} // namespace gooo
} // namespace open_spiel

#endif // OPEN_SPIEL_GAMES_GOOO_H_
