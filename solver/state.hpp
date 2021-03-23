#ifndef STATE_HPP
#define STATE_HPP

#include <iostream>
#include <string>
#include <vector>

#define FIRST_PLAYER_CHAR 'o'
#define SECOND_PLAYER_CHAR 'x'

struct State {
	int size;
	int points;
	int round;
	bool turn;
	bool end;
	std::vector<int> positions[2];

	State(int n)
	{
		size = n;
		points = 0;
		round = 0;
		turn = false;
		end = false;

		positions[0].resize(n, 0);
		positions[1].resize(n, 0);
	}

	bool operator ==(const State rhs) const;
	bool operator !=(const State rhs) const;

	friend std::ostream& operator << (std::ostream &out, const State &state);

	bool isWon();
	bool isMovePossible(int i);
	bool move(int i);
	std::vector<int> getPossibleMoves();
	void print();
};

#endif // STATE_HPP
