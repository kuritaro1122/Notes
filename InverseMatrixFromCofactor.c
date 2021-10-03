#include <stdio.h>
#include <math.h>

int main(void) {
    int size = 0;
    printf("正方行列の大きさ(s > 1):");
    scanf("%d", &size);
    printf("行列を入力してください。\n");
    int matrix[size][size];
    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            printf("[%d][%d]? ", i, j);
            scanf("%d", &matrix[i][j]);
            printf("\n");
        }
    }
    
    printf("size:%d\n", size);

    /*//入力の表示
    printf("入力の表示\n");
    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            printf("[%d][%d] : %d\n", i, j, matrix[i][j]);
        }
    }*/

    int cmatrix[size][size];
    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            int _size = size - 1;
            int _matrix[_size][_size];
            int x = 0;
            for (int k = 0; k < size; k++) {
                int y = 0;
                if (i == k) continue;
                for (int l = 0; l < size; l++) {
                    if (j == l) continue;
                    _matrix[x][y] = matrix[k][l];
                    y++;
                }
                x++;
                
            }
            if (_size <= 2) {
                int a = (_matrix[0][0] * _matrix[1][1]) - (_matrix[1][0] * _matrix[0][1]);
                int b = pow(-1, (i + j));
                cmatrix[j][i] = b * a;
            } else {
                int b = pow(-1, (i + j));
                int a = 0;
                for (int i = 0; i < _size; i++) {
                    int add = 1;
                    int dec = 1;
                    for (int j = 0; j < _size; j++) {
                        int x0 = (i + j) % _size;
                        int x1 = ((_size - 1) - (i + j)) % _size;
                        if (x1 < 0) x1 += 3;
                        int y = j % _size;
                        add *= _matrix[y][x0];
                        dec *= _matrix[y][x1];
                    }
                    a += add - dec;
                }
                
                cmatrix[j][i] = b * a;
            }
        }
    }

    printf("余因子行列\n");
    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            printf("[%d][%d]:%d\n", i, j, cmatrix[i][j]);
        }
    }

    int det = 0;
    for (int i = 0; i < size; i++) {
        det += matrix[0][i] * cmatrix[i][0];
    }
    printf("行列式:det = %d\n", det);

    printf("逆行列\n");
    float invMatrix[size][size];
    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            invMatrix[i][j] = (float)cmatrix[i][j] / (float)det;
            printf("[%d][%d]:%f\n", i, j, invMatrix[i][j]);
        }
    }
}
