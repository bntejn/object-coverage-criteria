/*
 *  This file contains an ISA-portable PIN tool for 
 *  measuring object branch coverage.
 *  http://stackoverflow.com/questions/36002452/how-to-generate-a-listing-of-branches-with-intel-pin-tool
 */

/* 
 * A Pin tool to help measuring object branch / condition coverage.
 *
 * @author Taejoon Byun <taejoon@umn.edu>
 *
 * last : Apr 5 2017
 * */

#include "pin.H"
#include <iostream>
#include <iomanip>
#include <fstream>
#include <sstream>
#include <string>
#include <map>
#include <bitset>
#include <cassert>

#define DEBUG 0
#define ENABLE_SETCC 1
#define ENABLE_CMOVCC 1
#define ENABLE_LOGICAL 1
#define ENABLE_BINARY 1

using namespace std;

class Conditional {
public:
    ADDRINT addr;
    /* {J: conditional jump, M: conditional move, S: set} */
    char type;
    long int taken;
    long int fallThrough;

    Conditional(char type, ADDRINT addr) {
        assert(type == 'J' || type == 'M' || type == 'S' || type == 'L' 
                || type == 'B');
        this->type = type;
        this->addr = addr;
        this->taken = 0;
        this->fallThrough = 0;
    }

    void take() {
        this->taken += 1;
    }

    void fall() {
        this->fallThrough += 1;
    }

    string str() {
        ostringstream ret;
        ret << type << ","<< showbase << hex << this->addr << "," << dec 
            << this->taken << "," << this->fallThrough << endl;
        return ret.str();
    }
};

map<ADDRINT, Conditional*> conditionMap;
ofstream outfile;

VOID countConditional(char type, ADDRINT ip, bool taken) {
    Conditional *b;
    if (ip > 0x700000000000ull) {
        return;
    }
    if (conditionMap.find(ip) == conditionMap.end()) {
        // new branch
        b = new Conditional(type, ip);
        conditionMap[ip] = b;
    } else {
        /* existing branch */
        b = conditionMap[ip];
    }
    if (taken) {
        b->take();
    } else {
        b->fall();
    }
    //cout<< conditionMap[ip]->str()<< endl;
}

/* x86 flags register: https://en.wikipedia.org/wiki/FLAGS_register 
 * x86 SETcc: http://x86.renejeschke.de/html/file_module_x86_id_288.html
 * REG union reference: https://software.intel.com/sites/landingpage/pintool/docs/62732/Pin/html/unionPIN__REGISTER.html 
 * https://software.intel.com/sites/landingpage/pintool/docs/56759/Pin/html/group__REG__CPU__IA32.html#g3b77029a2a445f70f0206dbad1e4e641
 */

#ifndef MY_REGISTER_MACRO
#define MY_REGISTER_MACRO
#define CF flags[0]
#define PF flags[2]
#define AF flags[4]
#define ZF flags[6]
#define SF flags[7]
#define TF flags[8]
#define OF flags[11]
#endif

bitset<16> getFlags(CONTEXT * ctxt) {
    ADDRINT val;
    PIN_GetContextRegval(ctxt, REG_FLAGS, reinterpret_cast<UINT8*>(&val));
    bitset<16> flags(val);
    //cout << REG_StringShort(REG_FLAGS) << ": " << flags << ", "<< flags[0]<< endl;
    return flags;
}

/* SETcc *********************************************************************/
void chkSeta(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, CF==0 && ZF==0);
}
void chkSetae(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, CF==0);
}
void chkSetb(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, CF==1);
}
void chkSetbe(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, CF==1 || ZF==1);
}
void chkSetc(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, CF==1);
}
void chkSete(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, ZF==1);
}
void chkSetg(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, ZF==0 && SF==OF);
}
void chkSetge(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, SF==OF);
}
void chkSetl(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, SF!=OF);
}
void chkSetle(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, ZF==1 || SF!=OF);
}
void chkSetna(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, CF==1 || ZF==1);
}
void chkSetnae(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, CF==1);
}
void chkSetnb(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, CF==0);
}
void chkSetnbe(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, CF==0 && ZF==0);
}
void chkSetnc(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, CF==0);
}
void chkSetne(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, ZF==0);
}
void chkSetng(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, ZF==1 || SF!=OF);
}
void chkSetnge(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, SF!=OF);
}
void chkSetnl(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, SF==OF);
}
void chkSetnle(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, ZF==0 && SF==OF);
}
void chkSetno(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, OF==0);
}
void chkSetnp(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, PF==0);
}
void chkSetns(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, SF==0);
}
void chkSetnz(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, ZF==0);
}
void chkSeto(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, OF==1);
}
void chkSetp(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, PF==1);
}
void chkSetpe(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, PF==1);
}
void chkSetpo(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, PF==0);
}
void chkSets(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, SF==1);
}
void chkSetz(ADDRINT ip, CONTEXT * ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('S', ip, ZF==1);
}

void treatSetcc(INS ins) {
    /* XED_ICLASS enum: https://software.intel.com/sites/landingpage/pintool/docs/65163/Xed/html/xed-iclass-enum_8h.html
     * INS_Category: http://people.cs.uchicago.edu/~xiliang/group__INS__BASIC__API__GEN__IA32.html#ga5ed09154017d06d6064ec98a66c8a18
     * x86 SETcc: http://x86.renejeschke.de/html/file_module_x86_id_288.html
     * FLAGS: https://software.intel.com/sites/landingpage/pintool/docs/49306/Pin/html/group__REG__CPU__IA32.html
     */
    /* SETcc instructions
     * XED_ICLASS_SETB, XED_ICLASS_SETBE, XED_ICLASS_SETL, XED_ICLASS_SETLE, 
     * XED_ICLASS_SETNB, XED_ICLASS_SETNBE, XED_ICLASS_SETNL, XED_ICLASS_SETNLE, 
     * XED_ICLASS_SETNO, XED_ICLASS_SETNP, XED_ICLASS_SETNS, XED_ICLASS_SETNZ, 
     * XED_ICLASS_SETO, XED_ICLASS_SETP, XED_ICLASS_SETS, XED_ICLASS_SETZ
     */
    //INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkTest, IARG_INST_PTR, IARG_CONTEXT, IARG_END);
    switch (INS_Opcode(ins)) {
        case XED_ICLASS_SETB:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkSetb,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_SETBE:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkSetbe,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_SETL:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkSetl,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_SETLE:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkSetle,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_SETNB:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkSetnb,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_SETNBE:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkSetnbe,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_SETNL:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkSetnl,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_SETNLE:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkSetnle,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_SETNO:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkSetno,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_SETNP:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkSetnp,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_SETNS:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkSetns,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_SETNZ:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkSetnz,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_SETO:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkSeto,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_SETP:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkSetp,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_SETS:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkSets,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_SETZ:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkSetz,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
    }
}

/* CMOVcc ********************************************************************/
void chkCfTrue(ADDRINT ip, CONTEXT *ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('M', ip, CF==1);
}
void chkCfTrueOrZfTrue(ADDRINT ip, CONTEXT *ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('M', ip, CF==1 || ZF==1);
}
void chkSfNeqOf(ADDRINT ip, CONTEXT *ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('M', ip, SF!=OF);
}
void chkZfTrueOrSfNeqOf(ADDRINT ip, CONTEXT *ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('M', ip, ZF==1 || SF!=OF);
}
void chkCfFalse(ADDRINT ip, CONTEXT *ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('M', ip, CF==0);
}
void chkCfFalseAndZfFalse(ADDRINT ip, CONTEXT *ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('M', ip, CF==0 && ZF==0);
}
void chkSfEqOf(ADDRINT ip, CONTEXT *ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('M', ip, SF==OF);
}
void chkZfFalseAndSfEqOf(ADDRINT ip, CONTEXT *ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('M', ip, ZF==0 && SF==OF);
}
void chkOfFalse(ADDRINT ip, CONTEXT *ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('M', ip, OF==0);
}
void chkPfFalse(ADDRINT ip, CONTEXT *ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('M', ip, PF==0);
}
void chkSfFalse(ADDRINT ip, CONTEXT *ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('M', ip, SF==0);
}
void chkZfFalse(ADDRINT ip, CONTEXT *ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('M', ip, ZF==0);
}
void chkOfTrue(ADDRINT ip, CONTEXT *ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('M', ip, OF==1);
}
void chkPfTrue(ADDRINT ip, CONTEXT *ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('M', ip, PF==1);
}
void chkZfTrue(ADDRINT ip, CONTEXT *ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('M', ip, ZF==1);
}

void chkLogical(ADDRINT ip, CONTEXT *ctxt) {
    //TODO
    bitset<16> flags = getFlags(ctxt);
    countConditional('L', ip, ZF==1);
}

void chkBinCfTrue(ADDRINT ip, CONTEXT *ctxt) {
    bitset<16> flags = getFlags(ctxt);
    countConditional('B', ip, CF==1);
}

void treatBinary(INS ins) {
    //TODO
    switch (INS_Opcode(ins)) {
        case XED_ICLASS_SBB:
            //SBB: http://x86.renejeschke.de/html/file_module_x86_id_286.html
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkBinCfTrue,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_ADC:
            //ADC: http://x86.renejeschke.de/html/file_module_x86_id_4.html
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkBinCfTrue,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
    }
}

void treatCmov(INS ins) {
      /* from: https://software.intel.com/sites/landingpage/pintool/docs/65163/Xed/html/xed-iclass-enum_8h.html
       *
       * cmovCC
       * XED_ICLASS_CMOVB, XED_ICLASS_CMOVBE, XED_ICLASS_CMOVL, 
       * XED_ICLASS_CMOVLE, XED_ICLASS_CMOVNB, XED_ICLASS_CMOVNBE, 
       * XED_ICLASS_CMOVNL, XED_ICLASS_CMOVNLE, XED_ICLASS_CMOVNO, 
       * XED_ICLASS_CMOVNP, XED_ICLASS_CMOVNS, XED_ICLASS_CMOVNZ, 
       * XED_ICLASS_CMOVO, XED_ICLASS_CMOVP, XED_ICLASS_CMOVS, 
       * XED_ICLASS_CMOVZ 
       *
       * fcmovCC
       * XED_ICLASS_FCMOVB, XED_ICLASS_FCMOVBE, XED_ICLASS_FCMOVE, 
       * XED_ICLASS_FCMOVNB, XED_ICLASS_FCMOVNBE, XED_ICLASS_FCMOVNE, 
       * XED_ICLASS_FCMOVNU, XED_ICLASS_FCMOVU
       * */
    switch (INS_Opcode(ins)) {
        case XED_ICLASS_CMOVB:
        case XED_ICLASS_FCMOVB:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkCfTrue,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_CMOVBE:
        case XED_ICLASS_FCMOVBE:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkCfTrueOrZfTrue,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_CMOVL:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkSfNeqOf,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_CMOVLE:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkZfTrueOrSfNeqOf,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_CMOVNB:
        case XED_ICLASS_FCMOVNB:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkCfFalse,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_CMOVNBE: 
        case XED_ICLASS_FCMOVNBE:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkCfFalseAndZfFalse,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_CMOVNL:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkSfEqOf,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_CMOVNLE:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkZfFalseAndSfEqOf,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_CMOVNO:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkOfFalse,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_CMOVNP:
        case XED_ICLASS_FCMOVNU:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkPfFalse,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_CMOVNS:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkSfFalse,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_CMOVNZ:
        case XED_ICLASS_FCMOVNE:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkZfFalse,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_CMOVO:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkOfTrue,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_CMOVP:
        case XED_ICLASS_FCMOVU:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkPfTrue,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
        case XED_ICLASS_CMOVS:
        case XED_ICLASS_CMOVZ:
        case XED_ICLASS_FCMOVE:
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)chkZfTrue,
                    IARG_INST_PTR, IARG_CONTEXT, IARG_END);
            break;
    }
}


VOID countConditionalJump(ADDRINT ip, VOID * taken) {
    countConditional('J', ip, (bool) taken);
}


// Is called for every instruction and instruments reads and writes
VOID Instruction(INS ins, VOID *v)
{
    if (INS_IsBranch(ins) && INS_HasFallThrough(ins)) {
        // a branch that has a fall-through
        INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)countConditionalJump, 
                IARG_INST_PTR, IARG_BRANCH_TAKEN, IARG_END);
    } 
#if ENABLE_SETCC
    if (INS_Category(ins) == XED_CATEGORY_SETCC) {
        /* Category: https://software.intel.com/sites/landingpage/xed/ref-manual/html/xed-category-enum_8h_source.html */
        treatSetcc(ins);
    } 
#endif
#if ENABLE_CMOVCC
    if (INS_Category(ins) == XED_CATEGORY_CMOV 
            || INS_Category(ins) == XED_CATEGORY_FCMOV) {
        /* Category: https://software.intel.com/sites/landingpage/xed/ref-manual/html/xed-category-enum_8h_source.html */
        treatCmov(ins);
    }
#endif
#if ENABLE_LOGICAL
    if (INS_Category(ins) == XED_CATEGORY_LOGICAL) {
        if (INS_Address(ins) > 0x700000000000ull) {
            return;
        }
        // https://software.intel.com/sites/landingpage/pintool/docs/53271/Pin/html/group__INS__BASIC__API__IA32.html#g556f7a38ca8ca40562d77810940f46b9
        // https://software.intel.com/sites/landingpage/pintool/docs/49306/Pin/html/group__INST__ARGS.html#gg7e2c955c99fa84246bb2bce1525b56818b1a445366074f7277035293fcc20c98
    #if DEBUG
        cout<< showbase<< hex<< INS_Address(ins)<< ":"; 
        cout<< setw(5)<< OPCODE_StringShort(INS_Opcode(ins));
        cout<< showbase<< "("<< hex<< setw(5)<< INS_Opcode(ins) << "), ";
        cout<< INS_OperandCount(ins)<< " operands: ";
        if (INS_OperandCount(ins) == 3) {
            cout<< "("<< INS_OperandReg(ins, 0)<< ", "<< INS_OperandReg(ins, 1)
                << ", "<< INS_OperandReg(ins, 2)<< ")"<< endl;
        } else if (INS_OperandCount(ins) == 2) {
            cout<< "("<< INS_OperandReg(ins, 0)<< ", "<< INS_OperandReg(ins, 1)
                << ")"<< endl;
        } else if (INS_OperandCount(ins) == 1) {
            cout<< "("<< INS_OperandReg(ins, 0)<< ")"<< endl;
        } else if (INS_OperandCount(ins) == 0){
            cout<< "[!] logical, no operand!"<< endl;
        }
    #endif
        INS_InsertCall(ins, IPOINT_AFTER, (AFUNPTR)chkLogical, IARG_INST_PTR, IARG_CONTEXT, IARG_END);
    }
#endif

#if ENABLE_BINARY
    if (INS_Category(ins) == XED_CATEGORY_BINARY) {
        treatBinary(ins);
    }
#endif


}

VOID Fini(INT32 code, VOID *v)
{
    typedef map<ADDRINT, Conditional*>::iterator itt;
    for (itt it=conditionMap.begin(); it!=conditionMap.end(); it++) {
        outfile << it->second->str();
    }
    outfile.close();
}

/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */
   
INT32 Usage()
{
    PIN_ERROR( "This Pintool prints a trace of memory addresses\n" 
              + KNOB_BASE::StringKnobSummary() + "\n");
    return -1;
}

KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool", "o", "pincov.out", 
        "specify output file name");

/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */

int main(int argc, char *argv[])
{
    if (PIN_Init(argc, argv)) return Usage();

    outfile.open(KnobOutputFile.Value().c_str());
    outfile << "type,addr,taken,fell"<< endl;    // title row

    INS_AddInstrumentFunction(Instruction, 0);
    PIN_AddFiniFunction(Fini, 0);

    // Never returns
    PIN_StartProgram();
    
    return 0;
}

