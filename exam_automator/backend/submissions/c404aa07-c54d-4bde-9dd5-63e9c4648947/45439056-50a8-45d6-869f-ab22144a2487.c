#include <stdio.h>
#include <stdlib.h>
#define ORDER 3

typedef struct BPlusNode {
    int data[ORDER];
    struct BPlusNode *child[ORDER + 1];
    int leaf, count;
    struct BPlusNode *next;
} BPlusNode;

BPlusNode *root = NULL;

BPlusNode* createNode(int leaf) {
    BPlusNode *n = malloc(sizeof(BPlusNode));
    n->leaf = leaf;
    n->count = 0;
    n->next = NULL;
    for (int i = 0; i <= ORDER; i++) n->child[i] = NULL;
    return n;
}

void insertBplus(int val) {
    if (!root) {
        root = createNode(1);
        root->data[0] = val;
        root->count = 1;
        return;
    }
    BPlusNode *t = root;
    while (!t->leaf) {
        int i;
        for (i = 0; i < t->count; i++)
            if (val < t->data[i]) break;
        t = t->child[i];
    }
    t->data[t->count++] = val;
}

void display(BPlusNode *node, int level) {
    if (node) {
        printf("Level %d [", level);
        for (int i = 0; i < node->count; i++) printf(" %d", node->data[i]);
        printf(" ]\n");
        if (!node->leaf)
            for (int i = 0; i <= node->count; i++)
                display(node->child[i], level + 1);
    }
}

int main() {
    int val, ch;
    while (1) {
        printf("\n1.Insert  2.Display  3.Exit\n");
        scanf("%d", &ch);
        if (ch == 1) {
            scanf("%d", &val);
            insertBplus(val);
            display(root, 0);
        } else if (ch == 2) display(root, 0);
        else break;
    }
    return 0;
}
