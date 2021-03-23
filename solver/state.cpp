#include "state.hpp"

std::ostream& operator << (std::ostream &out, const State &state)
{
	out << state.size << ' '
		<< state.round << ' '
		<< state.points << ' '
		<< state.turn << ' '
		<< state.end << ' ';
	for (int player = 0; player < 2; ++player) {
		for (int i = 0; i < state.size; ++i) {
			out << state.positions[player][i] << ' ';
		}
	}

	return out;
}

bool State::operator ==(const State rhs) const
{
	return (size == rhs.size and round == rhs.round and points == rhs.points and turn == rhs.turn and end == rhs.end and
			positions[0] == rhs.positions[0] and positions[1] == rhs.positions[1]);
}

bool State::operator !=(const State rhs) const
{
	return !(*this == rhs);
}

bool State::isWon()
{
	bool success = true;
	for (int position : positions[turn]) {
		if (position < size) {
			success = false;
			break;
		}
	}

	return success;
}

bool State::isMovePossible(int i)
{
	int position = positions[turn][i];
	return positions[turn][i] <= size and positions[1 - turn][position] != i + 1;
}

bool State::move(int i)
{
	bool success = false;
	if (!end and isMovePossible(i)) {
		success = true;
		round++;

		positions[turn][i]++;
		if (positions[turn][i] > size) {
			end = isWon();
		}

		turn = !turn;

		if (getPossibleMoves().empty()) {
			turn = !turn;
			points += 1 - 2 * turn;
		}
	}

	return success;
}

std::vector<int> State::getPossibleMoves()
{
	std::vector<int> possibleMoves;
	for (int i = 0; i < size; ++i) {
		if (isMovePossible(i)) {
			possibleMoves.push_back(i);
		}
	}

	return possibleMoves;
}

void State::print()
{
	std::vector<std::vector<char>> output;
	std::cout << round << ". turn, " << (turn ? SECOND_PLAYER_CHAR : FIRST_PLAYER_CHAR) << " to move. Points: " << points << "\n";
	for (int i = 0; i <= size; i++) {
		for (int j = 0; j <= size; j++) {
			char sign = ' ';
			if (i > 0 and j > 0) {
				sign = '.';
			}
			if (j > 0 and positions[1][j - 1] == i) {
				sign = 'x';
			}
			if (i > 0 and positions[0][i - 1] == j) {
				sign = 'o';
			}
			std::cout << sign;
		}
		std::cout << "\n";
	}
	std::cout << "\n";
}
