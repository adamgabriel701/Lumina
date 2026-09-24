; ModuleID = 'alloc_churn.ll'
source_filename = "alloc_churn.ll"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@__lumina_argc = local_unnamed_addr global i32 0
@__lumina_argv = local_unnamed_addr global ptr null
@str_0 = local_unnamed_addr constant [1 x i8] zeroinitializer
@str_1 = local_unnamed_addr constant [3 x i8] c"%s\00"
@str_2 = local_unnamed_addr constant [2 x i8] c" \00"
@str_3 = constant [4 x i8] c"%ld\00"
@str_4 = local_unnamed_addr constant [2 x i8] c"\0A\00"

; Function Attrs: nofree nounwind
declare noundef i32 @printf(ptr nocapture noundef readonly, ...) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nounwind willreturn allockind("alloc,uninitialized") allocsize(0) memory(inaccessiblemem: readwrite)
declare noalias noundef ptr @malloc(i64 noundef) local_unnamed_addr #1

; Function Attrs: mustprogress nounwind willreturn allockind("free") memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @free(ptr allocptr nocapture noundef) local_unnamed_addr #2

; Function Attrs: mustprogress nofree nounwind willreturn memory(argmem: read)
declare i64 @strlen(ptr nocapture) local_unnamed_addr #3

declare i64 @atoi(ptr) local_unnamed_addr

define noundef i32 @main(i32 %.1, ptr %.2) local_unnamed_addr {
main_entry:
  store i32 %.1, ptr @__lumina_argc, align 4
  store ptr %.2, ptr @__lumina_argv, align 8
  %argv_elem_ptr = getelementptr ptr, ptr %.2, i64 1
  %argv_elem = load ptr, ptr %argv_elem_ptr, align 8
  %len_str = tail call i64 @strlen(ptr noundef nonnull dereferenceable(1) %argv_elem)
  %icmp = icmp sgt i64 %len_str, 0
  br i1 %icmp, label %if_end, label %while_body.preheader

if_end:                                           ; preds = %main_entry
  %atoi_call = tail call i64 @atoi(ptr %argv_elem)
  %icmp.15 = icmp sgt i64 %atoi_call, 0
  br i1 %icmp.15, label %while_body.preheader, label %while_end

while_body.preheader:                             ; preds = %main_entry, %if_end
  %n.012 = phi i64 [ %atoi_call, %if_end ], [ 1000000, %main_entry ]
  br label %while_body

while_body:                                       ; preds = %while_body.preheader, %if_end.1
  %storemerge8 = phi i64 [ %add.3, %if_end.1 ], [ 0, %while_body.preheader ]
  %bitand27 = phi i64 [ %bitand, %if_end.1 ], [ 12345, %while_body.preheader ]
  %add.246 = phi i64 [ %add.23, %if_end.1 ], [ 0, %while_body.preheader ]
  %mul = mul nuw nsw i64 %bitand27, 1103515245
  %add = add nuw nsw i64 %mul, 12345
  %bitand = and i64 %add, 4294967295
  %ashr = lshr i64 %add, 16
  %mod = and i64 %ashr, 511
  %add.1 = add nuw nsw i64 %mod, 1
  %alloc_bytes_call = tail call ptr @malloc(i64 %add.1)
  %ptr_ne.not = icmp eq ptr %alloc_bytes_call, null
  br i1 %ptr_ne.not, label %if_end.1, label %if_then.1

while_end:                                        ; preds = %if_end.1, %if_end
  %add.24.lcssa = phi i64 [ 0, %if_end ], [ %add.23, %if_end.1 ]
  %putchar = tail call i32 @putchar(i32 32)
  %print_call.1 = tail call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) @str_3, i64 %add.24.lcssa)
  %putchar1 = tail call i32 @putchar(i32 10)
  ret i32 0

if_then.1:                                        ; preds = %while_body
  %idx_trunc = trunc i64 %storemerge8 to i8
  store i8 %idx_trunc, ptr %alloc_bytes_call, align 1
  %ptr_to_int = ptrtoint ptr %alloc_bytes_call to i64
  %black_box_call = tail call i64 asm sideeffect "", "=r,0"(i64 %ptr_to_int) #4
  %ptr_idx_load = load i8, ptr %alloc_bytes_call, align 1
  %idx_sext = sext i8 %ptr_idx_load to i64
  %add.2 = add i64 %add.246, %idx_sext
  tail call void @free(ptr nonnull %alloc_bytes_call)
  br label %if_end.1

if_end.1:                                         ; preds = %while_body, %if_then.1
  %add.23 = phi i64 [ %add.246, %while_body ], [ %add.2, %if_then.1 ]
  %add.3 = add nuw nsw i64 %storemerge8, 1
  %exitcond.not = icmp eq i64 %add.3, %n.012
  br i1 %exitcond.not, label %while_end, label %while_body
}

; Function Attrs: nofree nounwind
declare noundef i32 @putchar(i32 noundef) local_unnamed_addr #0

attributes #0 = { nofree nounwind }
attributes #1 = { mustprogress nofree nounwind willreturn allockind("alloc,uninitialized") allocsize(0) memory(inaccessiblemem: readwrite) "alloc-family"="malloc" }
attributes #2 = { mustprogress nounwind willreturn allockind("free") memory(argmem: readwrite, inaccessiblemem: readwrite) "alloc-family"="malloc" }
attributes #3 = { mustprogress nofree nounwind willreturn memory(argmem: read) }
attributes #4 = { nounwind }
