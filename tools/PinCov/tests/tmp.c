
#include <stdio.h>

struct reg {
    int word[10];
};

#define CF reg->word[0]

int main() {
    struct reg * reg = malloc(sizeof(struct reg));
    reg->word[0] = 2;
    printf("CF: %d\n", CF);
    return 0;
}
